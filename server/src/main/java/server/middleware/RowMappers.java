package server.middleware;

import java.sql.ResultSet;
import java.sql.SQLException;
import org.springframework.lang.NonNull;
import org.springframework.jdbc.core.RowMapper;
import server.models.Listing;
import server.models.User;
import server.models.Quote;
import server.models.Rating;


public class RowMappers {
    public static final class ListingRowMapper implements RowMapper<Listing> {
        @Override
        public Listing mapRow(@NonNull ResultSet rs, int rowNum) throws SQLException {
            return new Listing(
                        rs.getInt("listingId"),
                        rs.getInt("customerId"),
                        rs.getString("title"),
                        rs.getString("description"),
                        rs.getString("serviceRequired"),
                        rs.getString("status"),
                        rs.getString("location"),
                        rs.getString("createdAt")
                    );
        }
    }
    
    private static final class UserRowMapper implements RowMapper<User> {
        @Override
        public User mapRow(@NonNull ResultSet rs, int rowNum) throws SQLException {
            
            return new User(
                rs.getInt("userId"),
                rs.getString("email"),
                rs.getString("firstName"),
                rs.getString("lastName"),
                rs.getString("password"),
                rs.getString("role"),
                rs.getString("serviceOffered"),
                rs.getDate("createdAt")
            );
        }
    }
    
    private static final class QuoteRowMapper implements RowMapper<Quote> {
        @Override
        public Quote mapRow(@NonNull ResultSet rs, int rowNum) throws SQLException {
            return new Quote(
                        rs.getInt("quoteId"),
                        rs.getInt("listingId"),
                        rs.getInt("customerId"),
                        rs.getInt("soleTraderId"),
                        rs.getString("description"),
                        rs.getDouble("price"),
                        rs.getDate("date"),
                        rs.getString("status"),
                        rs.getDate("createdAt")
                    );
        }
    }

    private static final class RatingRowMapper implements RowMapper<Rating> {
        @Override
        public Rating mapRow(@NonNull ResultSet rs, int rowNum) throws SQLException {
            return new Rating(
                        rs.getInt("ratingId"),
                        rs.getInt("receiverId"),
                        rs.getInt("senderId"),
                        rs.getInt("rating"),
                        rs.getString("description"),
                        rs.getDate("createdAt")
                    );
        }
    }
    
    public static RowMapper<Rating> getRatingRowMapper() {
        return new RatingRowMapper();
    }

    public static RowMapper<Listing> getListingRowMapper() {
        return new ListingRowMapper();
    }
    
    public static RowMapper<User> getUserRowMapper() {
        return new UserRowMapper();
    }
    
    public static RowMapper<Quote> getQuoteRowMapper() {
        return new QuoteRowMapper();
    }
}
