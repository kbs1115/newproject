public class SimpleNetworkingTest {
    public static void main(String[] args) {

        new Thread(() -> new SimpleChatServer().go()).start();
        sleep(500);
        new Thread(() -> new PolylineEditorClient().go("TalkerA")).start();
        sleep(500);
        new Thread( () -> new PolylineEditorClient().go("TalkerB")).start();
        sleep(500);
        new Thread( () -> new PolylineEditorClient().go("TalkerC")).start();

    }
    private static void sleep(long t) {
        try {
            Thread.sleep(t);
        } catch (Exception ex) {
        }
    }
}