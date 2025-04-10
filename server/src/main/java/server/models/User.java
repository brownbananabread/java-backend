package server.models;

import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import java.util.Date;

@Entity
public class User {

    @Id
    private int userId;
    private String email;
    private String firstName;
    private String lastName;
    private String password;
    private String role;
    private String serviceOffered;
    private Date createdAt;

    public User(int userId, String email, String firstName, String lastName, String password, String role, String serviceOffered, Date createdAt) {
        this.userId = userId;
        this.email = email;
        this.firstName = firstName;
        this.lastName = lastName;
        this.password = password;
        this.role = role;
        this.serviceOffered = serviceOffered;
        this.createdAt = createdAt;
    }
    public User() {}

    // userId
    public int getUserId() { return userId; }
    public void setUserId(int userId) { this.userId = userId; }

    // email
    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }

    // firstName
    public String getFirstName() { return firstName; }
    public void setFirstName(String firstName) { this.firstName = firstName; }

    // lastName
    public String getLastName() { return lastName; }
    public void setLastName(String lastName) { this.lastName = lastName; }

    // password
    public String getPassword() { return password; }
    public void setPassword(String password) { this.password = password; }

    // role
    public String getRole() { return role; }
    public void setRole(String role) { this.role = role; }

    // serviceOffered
    public String getServiceOffered() { return serviceOffered; }
    public void setServiceOffered(String serviceOffered) { this.serviceOffered = serviceOffered; }

    // createdAt
    public Date getCreatedAt() { return createdAt; }
    public void setCreatedAt(Date createdAt) { this.createdAt = createdAt; }
}