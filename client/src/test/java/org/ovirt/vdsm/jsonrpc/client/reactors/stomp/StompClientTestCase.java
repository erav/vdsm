package org.ovirt.vdsm.jsonrpc.client.reactors.stomp;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNotNull;
import static org.ovirt.vdsm.jsonrpc.client.utils.JsonUtils.UTF8;

import java.io.IOException;
import java.util.concurrent.ArrayBlockingQueue;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.ovirt.vdsm.jsonrpc.client.ClientConnectionException;
import org.ovirt.vdsm.jsonrpc.client.reactors.ReactorClient;
import org.ovirt.vdsm.jsonrpc.client.reactors.ReactorClient.MessageListener;
import org.ovirt.vdsm.jsonrpc.client.reactors.ReactorListener;
import org.ovirt.vdsm.jsonrpc.client.reactors.ReactorListener.EventListener;

public class StompClientTestCase {
    private final static int TIMEOUT_SEC = 6;
    private final static String HOSTNAME = "localhost";
    private final static int PORT = 61626;
    private final static String MESSAGE = "Hello world!";
    private StompReactor listeningReactor;
    private StompReactor sendingReactor;

    @Before
    public void setUp() throws IOException {
        this.listeningReactor = new StompReactor();
        this.sendingReactor = new StompReactor();
    }

    @After
    public void tearDown() throws IOException {
        this.sendingReactor.close();
        this.listeningReactor.close();
    }

    @Test
    public void testEcho() throws InterruptedException, ExecutionException, ClientConnectionException {
        final BlockingQueue<byte[]> queue = new ArrayBlockingQueue<>(1);
        Future<ReactorListener> futureListener =
                this.listeningReactor.createListener(HOSTNAME, PORT, new EventListener() {

                    @Override
                    public void onAcccept(final ReactorClient client) {
                        client.addEventListener(new MessageListener() {
                            @Override
                            public void onMessageReceived(byte[] message) {
                                client.sendMessage(message);
                            }
                        });
                    }
                });

        ReactorListener listener = futureListener.get();
        assertNotNull(listener);

        ReactorClient client = this.sendingReactor.createClient(HOSTNAME, PORT);
        client.addEventListener(new ReactorClient.MessageListener() {

            @Override
            public void onMessageReceived(byte[] message) {
                queue.add(message);
            }
        });
        client.connect();

        client.sendMessage(MESSAGE.getBytes());
        byte[] message = queue.poll(TIMEOUT_SEC, TimeUnit.SECONDS);

        client.sendMessage(MESSAGE.getBytes());
        message = queue.poll(TIMEOUT_SEC, TimeUnit.SECONDS);

        client.close();
        listener.close();

        assertNotNull(message);
        assertEquals(MESSAGE, new String(message, UTF8));
    }
}
