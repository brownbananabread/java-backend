package server.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import server.models.User;
import server.service.QuoteService;
import server.utils.Response;
import java.util.Map;
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

        switch (user.getRole()) {
            case "soleTrader": return Response.Ok(quoteService.getAllQuotesPerUserId(user.getUserId()));
            case "customer": return Response.Ok(quoteService.getQuotesForCustomer(user.getUserId()));
            case "admin": return Response.Ok(quoteService.getAllQuotes());
            default: return Response.Unauthorized();
        }
    }

    @GetMapping("/quote/{quoteId}/accept")
    public ResponseEntity<?> acceptQuote(@CookieValue(name = "accessToken") String accessToken,
                                         @PathVariable int quoteId) {

        User user = request.getUserFromToken(accessToken);
        if (user == null) { return Response.Unauthorized(); }

        Quote quote = quoteService.getQuote(quoteId);
        if (quote == null) { return Response.Bad(Map.of("Message","Quote not found")); }

        if (user.getUserId() == quote.getCustomerId()) {
            quoteService.acceptQuoteAndCompleteListing(quoteId);
            return Response.Ok(Map.of("Message","Quote accepted"));
        } else {
            return Response.Unauthorized();
        }
    }

    @GetMapping("/quote/{quoteId}/reject")
    public ResponseEntity<?> rejectQuote(@CookieValue(name = "accessToken") String accessToken,
                                         @PathVariable int quoteId) {

        User user = request.getUserFromToken(accessToken);
        if (user == null) { return Response.Unauthorized(); }

        Quote quote = quoteService.getQuote(quoteId);
        if (quote == null) { return Response.Bad(Map.of("Message","Quote not found")); }

        if (user.getUserId() == quote.getCustomerId()) {
            quoteService.rejectQuote(quoteId);
            return Response.Ok(Map.of("Message","Quote accepted"));
        } else {
            return Response.Unauthorized();
        }
    }
}
