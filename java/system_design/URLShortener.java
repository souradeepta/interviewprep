import java.util.*;

public class URLShortener {
    private static final String BASE62 = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ";
    private long counter = 0;
    private Map<String, String> urlMap = new HashMap<>();
    private Map<String, String> reverseMap = new HashMap<>();

    public String shorten(String url) {
        if (reverseMap.containsKey(url)) {
            return reverseMap.get(url);
        }
        String code = encode(++counter);
        urlMap.put(code, url);
        reverseMap.put(url, code);
        return code;
    }

    public String expand(String code) {
        return urlMap.get(code);
    }

    private String encode(long num) {
        StringBuilder sb = new StringBuilder();
        while (num > 0) {
            sb.append(BASE62.charAt((int)(num % 62)));
            num /= 62;
        }
        return sb.reverse().toString();
    }

    public static void main(String[] args) {
        URLShortener shortener = new URLShortener();
        String url = "https://www.example.com/very/long/url/path";
        String short_code = shortener.shorten(url);
        System.out.println(url + " -> " + short_code);
        System.out.println("Expand: " + shortener.expand(short_code));
    }
}
