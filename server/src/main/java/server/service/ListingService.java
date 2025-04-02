
package server.service;

import org.springframework.stereotype.Service;
import server.models.Listing;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.jdbc.core.JdbcTemplate;

import java.util.List;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import server.middleware.RowMappers;


@Service
public class ListingService {
    private static final Logger logger = LoggerFactory.getLogger(ListingService.class);

    @Autowired
    private JdbcTemplate jdbcTemplate;

    public List<Listing> getActiveListingsForServiceType(String serviceType) {
        String sql = "SELECT * FROM listings WHERE serviceRequired = ? AND status = 'active'";
        List<Listing> listings = jdbcTemplate.query(sql, RowMappers.getListingRowMapper(), serviceType);
        
        return listings;
    }

    public List<Listing> getListingsForCustomer(Integer customerId) {
        String sql = "SELECT * FROM listings WHERE customerId = ?";
        List<Listing> listings = jdbcTemplate.query(sql, RowMappers.getListingRowMapper(), customerId);
        
        return listings;
    }













    // public List<Listing> getListings(Integer customerId) {
    //     String sql = "SELECT * FROM listings WHERE customerId = ?";
    //     List<Listing> listings = jdbcTemplate.query(sql, RowMappers.getListingRowMapper(), customerId);
        

    //     logger.info(listings.toString());
        
    //     return listings;
    // }

    // public Listing getListing(Integer cookieToken, Integer listingId) {
    //     String sql = "SELECT * FROM listings WHERE listingId = ?";
    //     List<Listing> listings = jdbcTemplate.query(sql, RowMappers.getListingRowMapper(), listingId);

    //     if (listings.isEmpty()) {
    //         return null;
    //     }

    //     Listing listing = listings.get(0);
        
        
    //     if (!listing.getCustomerId().equals(cookieToken)) {
    //         return null;
    //     }

    //     logger.info(listing.toString());
        
    //     return listing;
    // }

    // public void createListing(Integer customerId, String title, String description, String serviceRequired, String status, String location) {
    //     String sql = "INSERT INTO listings (customerId, title, description, serviceRequired, status, location) VALUES (?, ?, ?, ?, ?, ?)";
    //     jdbcTemplate.update(sql, customerId, title, description, serviceRequired, status, location);
    // }

}
