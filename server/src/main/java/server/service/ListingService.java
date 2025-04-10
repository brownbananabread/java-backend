
package server.service;

import org.springframework.stereotype.Service;
import server.models.Listing;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.jdbc.core.JdbcTemplate;
import java.util.List;
import server.middleware.RowMappers;

@Service
public class ListingService {

    @Autowired
    private JdbcTemplate jdbcTemplate;

    public List<Listing> getActiveListingsForServiceType(String serviceType) {
        String sql = "SELECT * FROM listings WHERE serviceRequired = ?";
        List<Listing> listings = jdbcTemplate.query(sql, RowMappers.getListingRowMapper(), serviceType);
        return listings.isEmpty() ? null : listings;
    }

    public List<Listing> getListingsForCustomer(int customerId) {
        String sql = "SELECT * FROM listings WHERE customerId = ?";
        List<Listing> listings = jdbcTemplate.query(sql, RowMappers.getListingRowMapper(), customerId);
        return listings.isEmpty() ? null : listings;
    }

    public List<Listing> getAllListings() {
        String sql = "SELECT * FROM listings";
        List<Listing> listings = jdbcTemplate.query(sql, RowMappers.getListingRowMapper());
        return listings.isEmpty() ? null : listings;
    }
}
