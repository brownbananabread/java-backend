package server.models;

import jakarta.persistence.Entity;
import jakarta.persistence.Id;

@Entity
public class Listing {

    @Id
    private Integer listingId;
    private Integer customerId;
    private String title;
    private String description;
    private String serviceRequired;
    private String status;
    private String location;

    public Listing(Integer listingId, Integer customerId, String title, String description, String serviceRequired, String status, String location) {
        this.listingId = listingId;
        this.customerId = customerId;
        this.title = title;
        this.description = description;
        this.serviceRequired = serviceRequired;
        this.status = status;
        this.location = location;
    }

    // Default constructor required by JPA
    public Listing() {
    }

    public Integer getListingId() {
        return listingId;
    }

    public void setListingId(Integer listingId) {
        this.listingId = listingId;
    }

    public Integer getCustomerId() {
        return customerId;
    }

    public void setCustomerId(Integer customerId) {
        this.customerId = customerId;
    }

    public String getTitle() {
        return title;
    }

    public void setTitle(String title) {
        this.title = title;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public String getServiceRequired() {
        return serviceRequired;
    }

    public void setServiceRequired(String serviceRequired) {
        this.serviceRequired = serviceRequired;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public String getLocation() {
        return location;
    }

    public void setLocation(String location) {
        this.location = location;
    }
}