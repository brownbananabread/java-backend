
package server.service;

import org.springframework.stereotype.Service;
import server.models.User;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.jdbc.core.JdbcTemplate;

import java.util.List;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import server.middleware.RowMappers;



@Service
public class UserService {
    private static final Logger logger = LoggerFactory.getLogger(UserService.class);

    @Autowired
    private JdbcTemplate jdbcTemplate;

    public User login(String email, String password) {
        String sql = "SELECT * FROM users WHERE email = ? AND password = ?";
        List<User> users = jdbcTemplate.query(sql, RowMappers.getUserRowMapper(), email, password);
        
        if (users.isEmpty()) {
            return null;
        }
        
        return users.get(0);
    }

    public User validate(String email) {
        String sql = "SELECT * FROM users WHERE email = ?";
        List<User> users = jdbcTemplate.query(sql, RowMappers.getUserRowMapper(), email);
        
        if (users.isEmpty()) {
            return null;
        }
        
        return users.get(0);
    }

    public User register(String firstName, String lastName, String email, String password, boolean isBusinessAccount) {
        String sql = "INSERT INTO users (email, firstName, lastName, password, isBusinessAccount) VALUES (?, ?, ?, ?, ?)";
        jdbcTemplate.update(sql, email, firstName, lastName, password, isBusinessAccount);

        return login(email, password);
    }
}