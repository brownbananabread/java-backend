package server.models;

import jakarta.persistence.Entity;

import java.util.Date;
import jakarta.persistence.Id;

@Entity
public class Quote {

    @Id
    private Integer quoteId;
    private Integer listingId;
    private Integer soleTraderId;
    private Integer customerId;
    private String description;
    private Double price;
    private Date date;
    private String status;
    private Date createdAt;

    public Quote(Integer quoteId, Integer listingId, Integer customerId, Integer soleTraderId, String description, 
                Double price, Date date, String status, Date createdAt) {
        this.quoteId = quoteId;
        this.listingId = listingId;
        this.customerId = customerId;
        this.soleTraderId = soleTraderId;
        this.description = description;
        this.price = price;
        this.date = date;
        this.status = status;
        this.createdAt = createdAt;
    }

    // Default constructor required by JPA
    public Quote() {
    }


    public Integer getCustomerId() {
        return customerId;
    }
    public void setCustomerId(Integer customerId) {
        this.customerId = customerId;
    }
    public Integer getQuoteId() {
        return quoteId;
    }

    public void setQuoteId(Integer quoteId) {
        this.quoteId = quoteId;
    }

    public Integer getListingId() {
        return listingId;
    }

    public void setListingId(Integer listingId) {
        this.listingId = listingId;
    }

    public Integer getSoleTraderId() {
        return soleTraderId;
    }

    public void setSoleTraderId(Integer soleTraderId) {
        this.soleTraderId = soleTraderId;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public Double getPrice() {
        return price;
    }

    public void setPrice(Double price) {
        this.price = price;
    }

    public Date getDate() {
        return date;
    }

    public void setDate(Date date) {
        this.date = date;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public Date getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(Date createdAt) {
        this.createdAt = createdAt;
    }
}