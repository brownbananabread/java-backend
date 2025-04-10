package server.models;

import jakarta.persistence.Entity;
import java.util.Date;
import jakarta.persistence.Id;

@Entity
public class Quote {

    @Id
    private int quoteId;
    private int listingId;
    private int soleTraderId;
    private int customerId;
    private String description;
    private Double price;
    private Date date;
    private String status;
    private Date createdAt;

    public Quote(int quoteId, int listingId, int customerId, int soleTraderId, String description, 
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

    public Quote() {}

    // quoteId
    public int getQuoteId() { return quoteId; }
    public void setQuoteId(int quoteId) { this.quoteId = quoteId; }

    // listingId
    public int getListingId() { return listingId; }
    public void setListingId(int listingId) { this.listingId = listingId; }

    // soleTraderId
    public int getSoleTraderId() { return soleTraderId; }
    public void setSoleTraderId(int soleTraderId) { this.soleTraderId = soleTraderId; }

    // customerId
    public int getCustomerId() { return customerId; }
    public void setCustomerId(int customerId) { this.customerId = customerId; }

    // description
    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }

    // price
    public Double getPrice() { return price; }
    public void setPrice(Double price) { this.price = price; }

    // date
    public Date getDate() { return date; }
    public void setDate(Date date) { this.date = date; }

    // status
    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }

    // createdAt
    public Date getCreatedAt() { return createdAt; }
    public void setCreatedAt(Date createdAt) { this.createdAt = createdAt; }
}