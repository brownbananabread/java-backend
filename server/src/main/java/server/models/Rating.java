package server.models;

import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import java.util.Date;

@Entity
public class Rating {

    @Id
    private int ratingId;
    private int receiverId;
    private int senderId;
    private int rating;
    private String description;
    private Date createdAt;

    public Rating(int ratingId, int receiverId, int senderId, int rating, String description, Date createdAt) {
        this.ratingId = ratingId;
        this.receiverId = receiverId;
        this.senderId = senderId;
        this.rating = rating;
        this.description = description;
        this.createdAt = createdAt;
    }

    public Rating() {}

    // ratingId
    public int getRatingId() { return ratingId; }
    public void setRatingId(int ratingId) { this.ratingId = ratingId; }

    // receiverId
    public int getReceiverId() { return receiverId; }
    public void setReceiverId(int receiverId) { this.receiverId = receiverId; }

    // senderId
    public int getSenderId() { return senderId; }
    public void setSenderId(int senderId) { this.senderId = senderId; }

    // rating
    public int getRating() { return rating; }
    public void setRating(int rating) { this.rating = rating; }

    // description
    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }

    // createdAt
    public Date getCreatedAt() { return createdAt; }
    public void setCreatedAt(Date createdAt) { this.createdAt = createdAt; }
}