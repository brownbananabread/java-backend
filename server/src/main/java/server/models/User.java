package server.models;

import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import java.util.Date;

@Entity
public class User {

    @Id
    private Integer userId;
    private String email;
    private String firstName;
    private String lastName;
    private String password;
    private boolean isSoleTrader;
    private int[] ratings;
    private String serviceOffered;
    private Date createdAt;

    public User(Integer userId, String email, String firstName, String lastName, String password, boolean isSoleTrader, int[] ratings, String serviceOffered, Date createdAt) {
        this.userId = userId;
        this.email = email;
        this.firstName = firstName;
        this.lastName = lastName;
        this.password = password;
        this.isSoleTrader = isSoleTrader;
        this.ratings = ratings;
        this.serviceOffered = serviceOffered;
        this.createdAt = createdAt;
    }
    public User() {
        // Default constructor for JPA
    }

    public Date getCreatedAt() {
        return createdAt;
    }
    public void setCreatedAt(Date createdAt) {
        this.createdAt = createdAt;
    }
    public String getServiceOffered() {
        return serviceOffered;
    }
    public void setServiceOffered(String serviceOffered) {
        this.serviceOffered = serviceOffered;
    }
    public int[] getRatings() {
        return ratings;
    }
    public void setRatings(int[] ratings) {
        this.ratings = ratings;
    }

    public String getEmail() {
        return email;
    }

    public String getFirstName() {
        return firstName;
    }

    public String getLastName() {
        return lastName;
    }

    public String getPassword() {
        return password;
    }

    public boolean isSoleTrader() {
        return isSoleTrader;
    }

    public Integer getUserId() {
        return userId;
    }

    public void setEmail(String email) {
        this.email = email;
    }

    public void setFirstName(String firstName) {
        this.firstName = firstName;
    }

    public void setLastName(String lastName) {
        this.lastName = lastName;
    }

    public void setPassword(String password) {
        this.password = password;
    }

    public void setSoleTrader(boolean isSoleTrader) {
        this.isSoleTrader = isSoleTrader;
    }

    public void setUserId(Integer userId) {
        this.userId = userId;
    }
}