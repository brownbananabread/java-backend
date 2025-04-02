package server.service;

import org.springframework.stereotype.Service;
import server.models.Quote;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.jdbc.core.JdbcTemplate;

import java.util.List;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import server.middleware.RowMappers;

@Service
public class QuoteService {
    private static final Logger logger = LoggerFactory.getLogger(QuoteService.class);

    @Autowired
    private JdbcTemplate jdbcTemplate;


    public List<Quote> getAllQuotesPerUserId(Integer userId) {
        String sql = "SELECT * FROM quotes WHERE soleTraderId = ?";
        List<Quote> quotes = jdbcTemplate.query(sql, RowMappers.getQuoteRowMapper(), userId);
        
        logger.info(quotes.toString());
        
        return quotes;
    }

    public List<Quote> getQuotesForCustomer(Integer customerId) {
        String sql = "SELECT * FROM quotes WHERE customerId = ?";
        List<Quote> quotes = jdbcTemplate.query(sql, RowMappers.getQuoteRowMapper(), customerId);
        
        logger.info(quotes.toString());
        
        return quotes;
    }

    public Quote getQuote(Integer quoteId) {
        String sql = "SELECT * FROM quotes WHERE quoteId = ?";
        List<Quote> quotes = jdbcTemplate.query(sql, RowMappers.getQuoteRowMapper(), quoteId);

        if (quotes.isEmpty()) {
            return null;
        }

        Quote quote = quotes.get(0);
        
        logger.info(quote.toString());
        
        return quote;
    }

    public void acceptQuoteAndCompleteListing(Integer quoteId) {
        String sql = "UPDATE quotes SET status = 'accepted' WHERE quoteId = ?";
        jdbcTemplate.update(sql, quoteId);

        String sql2 = "UPDATE listings SET status = 'complete' WHERE listingId = " +
            "(SELECT listingId FROM quotes WHERE quoteId = ?)";
        jdbcTemplate.update(sql2, quoteId);
    }

    public void rejectQuote(Integer quoteId) {
        String sql = "UPDATE quotes SET status = 'rejected' WHERE quoteId = ?";
        jdbcTemplate.update(sql, quoteId);
    }



    // public List<Quote> getAllQuotes(Integer quoteId) {
    //     String sql = "SELECT * FROM quotes WHERE quoteId = ?";
    //     List<Quote> quotes = jdbcTemplate.query(sql, RowMappers.getQuoteRowMapper(), quoteId);
        
    //     logger.info(quotes.toString());
        
    //     return quotes;
    // }

    // public Quote getQuote(Integer cookieToken, Integer quoteId) {
    //     String sql = "SELECT * FROM quotes WHERE quoteId = ?";
    //     List<Quote> quotes = jdbcTemplate.query(sql, RowMappers.getQuoteRowMapper(), quoteId);

    //     if (quotes.isEmpty()) {
    //         return null;
    //     }

    //     Quote quote = quotes.get(0);
        
    //     if (!quote.getSoleTraderId().equals(cookieToken)) {
    //         return null;
    //     }

    //     logger.info(quote.toString());
        
    //     return quote;
    // }

    // public void createQuote(Integer listingId, Integer soleTraderId, String description, Double price, Date date, String status) {
    //     String sql = "INSERT INTO quotes (listingId, soleTraderId, description, price, date, status) VALUES (?, ?, ?, ?, ?, ?)";
    //     jdbcTemplate.update(sql, listingId, soleTraderId, description, price, date, status);
    // }

    // public void acceptQuote(Integer quoteId) {
    //     String sql = "UPDATE quotes SET status = 'accepted' WHERE quoteId = ?";
    //     jdbcTemplate.update(sql, quoteId);

    //     String sql2 = "UPDATE listings SET status = 'complete' WHERE listingId = " +
    //         "(SELECT listingId FROM quotes WHERE quoteId = ?)";
    //     jdbcTemplate.update(sql2, quoteId);
    // }
}
