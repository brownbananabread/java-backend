package server.utils;

import org.springframework.http.ResponseEntity;
import java.util.Map;

public class Response {
    public static ResponseEntity<Map<String, String>> Unauthorized() {
        return ResponseEntity.status(401)
            .body(Map.of("Message", "UNAUTHORIZED"));
    }

    public static <T> ResponseEntity<T> Ok(T data) {
        return ResponseEntity.status(200)
            .body(data);
    }

    public static <T> ResponseEntity<T> Bad(T data) {
        return ResponseEntity.status(404)
            .body(data);
    }
}
