// Read-only developer capture of the focused Roadium window on a secondary user.
import android.accessibilityservice.AccessibilityServiceInfo;
import android.app.UiAutomation;
import android.graphics.Rect;
import android.os.HandlerThread;
import android.os.Looper;
import android.util.Xml;
import android.view.accessibility.AccessibilityNodeInfo;
import android.view.accessibility.AccessibilityWindowInfo;
import java.lang.reflect.Constructor;
import java.lang.reflect.Method;
import org.xmlpull.v1.XmlSerializer;

public final class RoadiumUiDump {
  private static final String PACKAGE = "io.github.musicpizzaman.roadium";
  private static boolean contains(AccessibilityNodeInfo n, String text) {
    if (n == null) return false;
    if (text.equals(String.valueOf(n.getText()))) return true;
    for (int i = 0; i < n.getChildCount(); i++)
      if (contains(n.getChild(i), text)) return true;
    return false;
  }
  private static void node(XmlSerializer out, AccessibilityNodeInfo n) throws Exception {
    if (n == null || !n.isVisibleToUser()) return;
    Rect bounds = new Rect(); n.getBoundsInScreen(bounds);
    if (bounds.isEmpty()) return;
    out.startTag(null, "node");
    out.attribute(null, "package", String.valueOf(n.getPackageName()));
    out.attribute(null, "text", n.getText() == null ? "" : n.getText().toString());
    out.attribute(null, "content-desc", n.getContentDescription() == null ? "" : n.getContentDescription().toString());
    out.attribute(null, "class", String.valueOf(n.getClassName()));
    out.attribute(null, "bounds", "["+bounds.left+","+bounds.top+"]["+bounds.right+","+bounds.bottom+"]");
    out.attribute(null, "scrollable", String.valueOf(n.isScrollable()));
    out.attribute(null, "enabled", String.valueOf(n.isEnabled()));
    out.attribute(null, "checkable", String.valueOf(n.isCheckable()));
    out.attribute(null, "checked", String.valueOf(n.isChecked()));
    out.attribute(null, "clickable", String.valueOf(n.isClickable()));
    for (int i = 0; i < n.getChildCount(); i++) node(out, n.getChild(i));
    out.endTag(null, "node");
  }
  public static void main(String[] args) throws Exception {
    HandlerThread thread = new HandlerThread("RoadiumDeveloperUiCapture");
    thread.start();
    UiAutomation automation = null;
    boolean connected = false;
    try {
      Class<?> connection = Class.forName("android.app.UiAutomationConnection");
      Class<?> iface = Class.forName("android.app.IUiAutomationConnection");
      Constructor<UiAutomation> ctor = UiAutomation.class.getDeclaredConstructor(Looper.class, iface);
      ctor.setAccessible(true);
      automation = ctor.newInstance(thread.getLooper(), connection.getDeclaredConstructor().newInstance());
      Method connect = UiAutomation.class.getDeclaredMethod("connect", int.class);
      connect.setAccessible(true); connect.invoke(automation, 1);
      connected = true;
      AccessibilityServiceInfo info = automation.getServiceInfo();
      info.flags |= AccessibilityServiceInfo.FLAG_RETRIEVE_INTERACTIVE_WINDOWS
          | AccessibilityServiceInfo.FLAG_INCLUDE_NOT_IMPORTANT_VIEWS;
      automation.setServiceInfo(info);
      AccessibilityNodeInfo chosen = null;
      int best = Integer.MIN_VALUE;
      for (AccessibilityWindowInfo window : automation.getWindows()) {
        AccessibilityNodeInfo root = window.getRoot();
        if (root == null || !PACKAGE.equals(String.valueOf(root.getPackageName()))) continue;
        int score = window.getLayer() + (window.isFocused() ? 1000 : 0)
            + (contains(root, "Local filter diagnostics") ? 100000 : 0);
        if (score > best) { chosen = root; best = score; }
      }
      if (chosen == null) throw new IllegalStateException("No Roadium window available");
      XmlSerializer out = Xml.newSerializer();
      out.setOutput(System.out, "UTF-8"); out.startDocument("UTF-8", true);
      out.startTag(null, "hierarchy"); node(out, chosen); out.endTag(null, "hierarchy");
      out.endDocument(); out.flush();
    } finally {
      if (connected) {
        Method disconnect = UiAutomation.class.getDeclaredMethod("disconnect");
        disconnect.setAccessible(true); disconnect.invoke(automation);
      }
      thread.quitSafely();
    }
  }
}
