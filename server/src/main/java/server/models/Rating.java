package server.models;

import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import java.util.Date;

@Entity
public class Rating {

    @Id
    private Integer ratingId;
    private Integer receiverId;
    private Integer senderId;
    private Integer rating;
    private Date createdAt;

    public Rating(Integer ratingId, Integer receiverId, Integer senderId, Integer rating, Date createdAt) {
        this.ratingId = ratingId;
        this.receiverId = receiverId;
        this.senderId = senderId;
        this.rating = rating;
        this.createdAt = createdAt;
    }

    public Rating() {}

    // ratingId
    public Integer getRatingId() { return ratingId; }
    public void setRatingId(Integer ratingId) { this.ratingId = ratingId; }

    // receiverId
    public Integer getReceiverId() { return receiverId; }
    public void setReceiverId(Integer receiverId) { this.receiverId = receiverId; }

    // senderId
    public Integer getSenderId() { return senderId; }
    public void setSenderId(Integer senderId) { this.senderId = senderId; }

    // rating
    public Integer getRating() { return rating; }
    public void setRating(Integer rating) { this.rating = rating; }

    // createdAt
    public Date getCreatedAt() { return createdAt; }
    public void setCreatedAt(Date createdAt) { this.createdAt = createdAt; }
}