import java.util.*;

interface Observer { void update(Button b); }

class Button {
    List<Observer> observers = new ArrayList<>();
    boolean pressed;
    void attach(Observer o) { observers.add(o); }
    void detach(Observer o) { observers.remove(o); }
    void notify_obs() { for(Observer o : observers) o.update(this); }
    void press() { pressed=true; notify_obs(); }
    void release() { pressed=false; notify_obs(); }
}

class LogObserver implements Observer {
    public void update(Button b) { System.out.println("Button: " + (b.pressed ? "pressed" : "released")); }
}

public class ObserverPattern {
    public static void main(String[] args) {
        Button btn = new Button();
        btn.attach(new LogObserver());
        btn.press();
        btn.release();
    }
}
