package server.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseCookie;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import server.models.User;
import server.service.UserService;
import org.springframework.http.HttpHeaders;
import server.utils.Response;
import server.middleware.Request;
import java.util.Map;

@RestController
@RequestMapping("/api")
public class UserController {

    @Autowired
    private UserService userService;

    @Autowired
    private Request request;

    @PostMapping("/login")
    public ResponseEntity<?> login(@RequestBody Map<String, String> body) {
        String email = body.get("email");
        String password = body.get("password");

        if (email == null || password == null) { return Response.Bad(Map.of("Message", "Email and password are required")); }

        User user = userService.login(email, password);
        if (user == null) { return Response.Bad(Map.of("Message","Email or password are unvalid")); }

        String accessToken = String.valueOf(user.getUserId()); // Assuming userId is the accessToken

        ResponseCookie cookie = ResponseCookie.from("accessToken", accessToken)
            .httpOnly(false)
            .path("/")
            .maxAge(24 * 60 * 60) // 1 day in seconds
            .domain("") // Set your domain or leave empty for current domain
            .secure(false) // Set to true in production with HTTPS
            .sameSite("Lax") // Less restrictive than Strict
            .build();

        return ResponseEntity.ok()
            .header(HttpHeaders.SET_COOKIE, cookie.toString())
            .body(user);
    }

    @GetMapping("/validate")
    public ResponseEntity<?> validate(@RequestParam String email) {
        if (email == null) { return Response.Bad(Map.of("Message","Email is required")); }

        User user = userService.validate(email);
        if (user == null) { return Response.Bad(Map.of("Message","Email is invalid")); }

        return Response.Ok(Map.of("Message","Email is valid"));
    }

    @PostMapping("/register")
    public ResponseEntity<?> register(@RequestBody Map<String, String> credentials) {
        String firstName = credentials.get("firstName");
        String lastName = credentials.get("lastName");
        String email = credentials.get("email");
        String password = credentials.get("password");
        String role = credentials.get("role");

        if (firstName == null || lastName == null || email == null || password == null || role == null) {
            return Response.Bad(Map.of("Message","All fields are required"));
        }

        User user = userService.register(firstName, lastName, email, password, role);

        String accessToken = String.valueOf(user.getUserId());

        ResponseCookie cookie = ResponseCookie.from("accessToken", accessToken)
        .httpOnly(false)
        .path("/")
        .maxAge(24 * 60 * 60) // 1 day in seconds
        .domain("") // Set your domain or leave empty for current domain
        .secure(false) // Set to true in production with HTTPS
        .sameSite("Lax") // Less restrictive than Strict
        .build();
    
        return ResponseEntity.ok()
            .header(HttpHeaders.SET_COOKIE, cookie.toString())
            .body(user);
    }

    @GetMapping("/profile")
    public ResponseEntity<?> getProfileFromToken(@CookieValue(name = "accessToken") String accessToken) {
        User user = request.getUserFromToken(accessToken);
        if (user == null) { return Response.Unauthorized(); }

        return Response.Ok(user);
    }

    @GetMapping("/users")
    public ResponseEntity<?> getAllUsers(@CookieValue(name = "accessToken") String accessToken, 
                                         @RequestParam(required = false) String service) {
        
        User user = request.getUserFromToken(accessToken);
        if (user == null) { return Response.Unauthorized(); }

        switch (user.getRole()) {
            case "admin": return Response.Ok(userService.getAllUsers());
            case "customer": return Response.Ok(userService.getSoleTraders(service));
            case "soleTrader": return Response.Ok(userService.getSoleTraders(service));
            default: return Response.Unauthorized();
        }
    }
}
