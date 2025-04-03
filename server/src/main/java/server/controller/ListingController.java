package server.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import server.service.ListingService;
import server.middleware.Request;
import server.utils.Response;
import server.models.User;

@RestController
@RequestMapping("/api")
public class ListingController {

    @Autowired
    private ListingService listingService;
    
    @Autowired
    private Request request;
    
    @GetMapping("/listings")
    public ResponseEntity<?> getListings(@CookieValue(name = "accessToken") String accessToken) {

        User user = request.getUserFromToken(accessToken);

        if (user == null) {
            return Response.Unauthorized();
        }

        switch (user.getRole()) {
            case "soleTrader": return Response.Ok(listingService.getActiveListingsForServiceType(user.getServiceOffered()));
            case "customer": return Response.Ok(listingService.getListingsForCustomer(user.getUserId()));
            case "admin": return Response.Ok(listingService.getAllListings());
            default: return Response.Unauthorized();
        }
    }
}
