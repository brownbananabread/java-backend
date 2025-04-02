package server.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;


import server.models.User;
import server.service.QuoteService;
import server.utils.Response;

import java.util.List;
import server.middleware.Request;
import server.models.Quote;

@RestController
@RequestMapping("/api")
public class QuoteController {

    @Autowired
    private QuoteService quoteService;

    @Autowired
    private Request request;


    @GetMapping("/quotes")
    public ResponseEntity<?> getQuotes(@CookieValue(name = "accessToken") String accessToken) {

        User user = request.getUserFromToken(accessToken);

        if (user == null) {
            return Response.Unauthorized();
        }

        if (user.isSoleTrader()) {
            List<Quote> quotes = quoteService.getAllQuotesPerUserId(user.getUserId());
            return Response.Ok(quotes);
        } else {
            List<Quote> quotes = quoteService.getQuotesForCustomer(user.getUserId());
            return Response.Ok(quotes);
        } 
    }

    @GetMapping("/quote/{quoteId}/accept")
    public ResponseEntity<?> acceptQuote(@CookieValue(name = "accessToken") String accessToken,
                                         @PathVariable Integer quoteId) {

        User user = request.getUserFromToken(accessToken);

        if (user == null) {
            return Response.Unauthorized();
        }

        Quote quote = quoteService.getQuote(quoteId);

        if (quote == null) {
            return Response.Bad("Quote not found");
        }

        if (user.getUserId() == quote.getCustomerId()) {
            quoteService.acceptQuoteAndCompleteListing(quoteId);
            return Response.Ok("Quote accepted");
        } else {
            return Response.Unauthorized();
        }
    }

    @GetMapping("/quote/{quoteId}/reject")
    public ResponseEntity<?> rejectQuote(@CookieValue(name = "accessToken") String accessToken,
                                         @PathVariable Integer quoteId) {

        User user = request.getUserFromToken(accessToken);

        if (user == null) {
            return Response.Unauthorized();
        }

        Quote quote = quoteService.getQuote(quoteId);

        if (quote == null) {
            return Response.Bad("Quote not found");
        }

        if (user.getUserId() == quote.getCustomerId()) {
            quoteService.rejectQuote(quoteId);
            return Response.Ok("Quote rejected");
        } else {
            return Response.Unauthorized();
        }
    }









    // @GetMapping("/quote/{quoteId}")
    // public ResponseEntity<?> getQuote(@CookieValue(name = "accessToken", required = false) Integer cookieToken,
    //                                    @PathVariable Integer quoteId) {

    //     if (cookieToken == null) {
    //         return ResponseEntity.status(401).body(Map.of("message", "Unauthorized"));
    //     }

    //     var quote = quoteService.getQuote(cookieToken, quoteId);

    //     if (quote == null) {
    //         return ResponseEntity.status(404).body(Map.of("message", "Quote not found"));
    //     }

    //     return ResponseEntity.ok(quote);
    // }

    // @PostMapping("/quote")
    // public ResponseEntity<?> createQuote(
    //     @CookieValue(name = "accessToken", required = false) Integer cookieToken, 
    //     @RequestBody Map<String, String> body) {

    //     if (cookieToken == null) {
    //         return ResponseEntity.status(401).body(Map.of("message", "Unauthorized"));
    //     }

    //     Integer soleTraderId = cookieToken;
    //     Integer listingId = Integer.valueOf(body.get("listingId"));
    //     String description = body.get("description");
    //     Double price = Double.valueOf(body.get("price"));
    //     String status = body.get("status");
    //     Date date = Date.valueOf(body.get("date"));

    //     quoteService.createQuote(listingId, soleTraderId, description, price, date, status);

    //     return ResponseEntity.status(201).build();
    // }

    // @GetMapping("/quote/{quoteId}/accept")
    // public ResponseEntity<?> acceptQuote(
    //     @CookieValue(name = "accessToken", required = false) Integer cookieToken, 
    //     @PathVariable Integer quoteId) {

    //     if (cookieToken == null) {
    //         return ResponseEntity.status(401).body(Map.of("message", "Unauthorized"));
    //     }

    //     quoteService.acceptQuote(quoteId);

    //     return ResponseEntity.status(201).build();
    // }
}
