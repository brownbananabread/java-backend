package server.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseCookie;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import server.models.User;
import server.service.UserService;

import org.springframework.http.HttpHeaders;

import server.utils.Response;

import java.util.Map;

@RestController
@RequestMapping("/api")
public class AuthController {

    @Autowired
    private UserService authService;

    @PostMapping("/login")
    public ResponseEntity<?> login(@RequestBody Map<String, String> credentials) {
        String email = credentials.get("email");
        String password = credentials.get("password");

        if (email == null || password == null) {
            return Response.Bad("Email and password are required");
        }

        User user = authService.login(email, password);

        if (user == null) {
            return Response.Bad("Email or password are unvalid");
        }

        String userToken = String.valueOf(user.getUserId());

        ResponseCookie cookie = ResponseCookie.from("accessToken", userToken)
        .httpOnly(false)  // Setting HttpOnly to false to allow JavaScript access
        .path("/")
        .secure(true)     // Recommended for security if your site uses HTTPS
        .sameSite("Strict")  // Helps prevent CSRF attacks
        .build();

        return ResponseEntity.ok()
            .header(HttpHeaders.SET_COOKIE, cookie.toString())
            .body(user);
    }

    @GetMapping("/validate")
    public ResponseEntity<?> validate(@RequestParam String email) {
        if (email == null) {
            return Response.Bad("Email is required");
        }

        User user = authService.validate(email);

        if (user == null) {
            return Response.Bad("Email is invalid");
        }

        return Response.Ok("Email is valid");
    }

    @PostMapping("/register")
    public ResponseEntity<?> register(@RequestBody Map<String, String> credentials) {
        String firstName = credentials.get("firstName");
        String lastName = credentials.get("lastName");
        String email = credentials.get("email");
        String password = credentials.get("password");
        Boolean isSoleTrader = Boolean.valueOf(credentials.get("isSoleTrader"));

        if (firstName == null || lastName == null || email == null || password == null || isSoleTrader == null) {
            return Response.Bad("All fields are required");
        }

        User user = authService.register(firstName, lastName, email, password, isSoleTrader);

        String userToken = String.valueOf(user.getUserId());

        ResponseCookie cookie = ResponseCookie.from("accessToken", userToken)
        .httpOnly(false)  // Setting HttpOnly to false to allow JavaScript access
        .path("/")
        .secure(true)     // Recommended for security if your site uses HTTPS
        .sameSite("Strict")  // Helps prevent CSRF attacks
        .build();
    
        // Return response with cookie in header
        return ResponseEntity.ok().header(HttpHeaders.SET_COOKIE, cookie.toString()).body(user);
    }
}
