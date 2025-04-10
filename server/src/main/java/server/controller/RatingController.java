package server.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import server.service.RatingService;
import server.middleware.Request;
import server.utils.Response;
import java.util.Map;
import java.util.List;
import server.models.User;
import server.models.Rating;

@RestController
@RequestMapping("/api")
public class RatingController {

    @Autowired
    private RatingService ratingService;
    
    @Autowired
    private Request request;

    @GetMapping("/ratings")
    public ResponseEntity<?> getRatings(@CookieValue(name = "accessToken") String accessToken) {

        User user = request.getUserFromToken(accessToken);
        if (user == null) { return Response.Unauthorized(); }

        List<Rating> ratings = ratingService.getRatingsForUser(user.getUserId());
        if (ratings == null) { return Response.Bad(Map.of("Message","No ratings found")); }

        return Response.Ok(ratings);
    }

    @PostMapping("/ratings")
    public ResponseEntity<?> getRatings(@CookieValue(name = "accessToken") String accessToken,
                                    @RequestBody Map<String, String> body) {
        User user = request.getUserFromToken(accessToken);
        if (user == null) { return Response.Unauthorized(); }
        
        String userId = body.get("userId");
        String ratingStr = body.get("rating");
        String description = body.get("description");
        
        if (userId == null || ratingStr == null) {
            return Response.Bad(Map.of("Message","Invalid request"));
        }
        
        try {
            int rating = Integer.parseInt(ratingStr);
            if (rating < 1 || rating > 5) {
                return Response.Bad(Map.of("Message", "Rating must be between 1 and 5"));
            }
            
            User receiver = request.getUserFromToken(userId);
            if (receiver == null) { return Response.Unauthorized(); }
            
            ratingService.rateUser(receiver.getUserId(), rating, user.getUserId(), description);
            return Response.Ok(Map.of("Message","Rating added successfully"));
        } catch (NumberFormatException e) {
            return Response.Bad(Map.of("Message", "Rating must be a valid number"));
        }
    }
}
