package server.models;

import jakarta.persistence.Entity;
import jakarta.persistence.Id;

@Entity
public class Listing {

    @Id
    private int listingId;
    private int customerId;
    private String title;
    private String description;
    private String serviceRequired;
    private String status;
    private String location;
    private String createdAt;

    public Listing(int listingId, int customerId, String title, String description, String serviceRequired, String status, String location, String createdAt) {
        this.listingId = listingId;
        this.customerId = customerId;
        this.title = title;
        this.description = description;
        this.serviceRequired = serviceRequired;
        this.status = status;
        this.location = location;
        this.createdAt = createdAt;
    }

    public Listing() {}

    
    // listingId
    public int getListingId() { return listingId; }
    public void setListingId(int listingId) { this.listingId = listingId; }

    // customerId
    public int getCustomerId() { return customerId; }
    public void setCustomerId(int customerId) { this.customerId = customerId; }

    // title
    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }

    // description
    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }

    // serviceRequired
    public String getServiceRequired() { return serviceRequired; }
    public void setServiceRequired(String serviceRequired) { this.serviceRequired = serviceRequired; }

    // status
    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }

    // location
    public String getLocation() { return location; }
    public void setLocation(String location) { this.location = location; }

    // createdAt
    public String getCreatedAt() { return createdAt; }
    public void setCreatedAt(String createdAt) { this.createdAt = createdAt; }
}