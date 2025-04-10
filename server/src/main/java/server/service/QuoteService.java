package server.service;

import org.springframework.stereotype.Service;
import server.models.Quote;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.jdbc.core.JdbcTemplate;
import java.util.List;
import server.middleware.RowMappers;

@Service
public class QuoteService {

    @Autowired
    private JdbcTemplate jdbcTemplate;

    public List<Quote> getAllQuotesPerUserId(int userId) {
        String sql = "SELECT * FROM quotes WHERE soleTraderId = ?";
        List<Quote> quotes = jdbcTemplate.query(sql, RowMappers.getQuoteRowMapper(), userId);
        return quotes.isEmpty() ? null : quotes;
    }

    public List<Quote> getQuotesForCustomer(int customerId) {
        String sql = "SELECT * FROM quotes WHERE customerId = ?";
        List<Quote> quotes = jdbcTemplate.query(sql, RowMappers.getQuoteRowMapper(), customerId);
        return quotes.isEmpty() ? null : quotes;
    }

    public Quote getQuote(int quoteId) {
        String sql = "SELECT * FROM quotes WHERE quoteId = ?";
        List<Quote> quotes = jdbcTemplate.query(sql, RowMappers.getQuoteRowMapper(), quoteId);
        return quotes.isEmpty() ? null : quotes.get(0);
    }

    public void acceptQuoteAndCompleteListing(int quoteId) {
        String sql = "UPDATE quotes SET status = 'accepted' WHERE quoteId = ?";
        jdbcTemplate.update(sql, quoteId);

        String sql2 = "UPDATE listings SET status = 'complete' WHERE listingId = " +
            "(SELECT listingId FROM quotes WHERE quoteId = ?)";
        jdbcTemplate.update(sql2, quoteId);
    }

    public void rejectQuote(int quoteId) {
        String sql = "UPDATE quotes SET status = 'rejected' WHERE quoteId = ?";
        jdbcTemplate.update(sql, quoteId);
    }

    public List<Quote> getAllQuotes() {
        String sql = "SELECT * FROM quotes";
        List<Quote> quotes = jdbcTemplate.query(sql, RowMappers.getQuoteRowMapper());
        return quotes.isEmpty() ? null : quotes;
    }
}
