package server.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import server.models.Listing;
import server.service.ListingService;
import server.middleware.Request;
import server.utils.Response;
import java.util.List;
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

        if (user.isSoleTrader()) {
            List<Listing> listings = listingService.getActiveListingsForServiceType(user.getServiceOffered());
            return Response.Ok(listings);
        } else {
            List<Listing> listings = listingService.getListingsForCustomer(user.getUserId());
            return Response.Ok(listings);
        } 
    }
}










    // @GetMapping("/listings")
    
    // public ResponseEntity<?> getListings(@CookieValue(name = "accessToken", required = false) Integer userToken) {

    //     if (userToken == null) {
    //         return ResponseEntity.status(401).body(Map.of("message", "Unauthorized"));
    //     }

    //     var listings = listingService.getListings(userToken);
        
    //     return ResponseEntity.ok(listings);
    // }


    // @GetMapping("/listing/{listingId}")
    // public ResponseEntity<?> getListing(@CookieValue(name = "accessToken", required = false) Integer cookieToken,
    //                                    @PathVariable Integer listingId) {

    //     if (cookieToken == null) {
    //         return ResponseEntity.status(401).body(Map.of("message", "Unauthorized"));
    //     }

    //     var listing = listingService.getListing(cookieToken, listingId);

    //     if (listing == null) {
    //         return ResponseEntity.status(404).body(Map.of("message", "Listing not found"));
    //     }

    //     return ResponseEntity.ok(listing);
    // }

    // @PostMapping("/listing")
    // public ResponseEntity<?> createListing(
    //     @CookieValue(name = "accessToken", required = false) String cookieToken, 
    //     @RequestBody Map<String, String> body) {

    //     if (cookieToken == null) {
    //         return ResponseEntity.status(401).body(Map.of("message", "Unauthorized"));
    //     }

    //     String customerId = cookieToken;
    //     String title = body.get("title");
    //     String description = body.get("description");
    //     String serviceRequired = body.get("serviceRequired");
    //     String status = body.get("status");
    //     String location = body.get("location");

    //     listingService.createListing(Integer.parseInt(customerId), title, description, serviceRequired, status, location);

    //     return ResponseEntity.status(201).build();
    // }
