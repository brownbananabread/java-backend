
package server.service;

import org.springframework.stereotype.Service;
import server.models.User;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.jdbc.core.JdbcTemplate;
import java.util.List;
import server.middleware.RowMappers;

@Service
public class UserService {

    @Autowired
    private JdbcTemplate jdbcTemplate;

    public User login(String email, String password) {
        String sql = "SELECT * FROM users WHERE email = ? AND password = ?";
        List<User> users = jdbcTemplate.query(sql, RowMappers.getUserRowMapper(), email, password);
        return users.isEmpty() ? null : users.get(0);
    }

    public User validate(String email) {
        String sql = "SELECT * FROM users WHERE email = ?";
        List<User> users = jdbcTemplate.query(sql, RowMappers.getUserRowMapper(), email);
        return users.isEmpty() ? null : users.get(0);
    }

    public User register(String firstName, String lastName, String email, String password, String role) {
        String sql = "INSERT INTO users (email, firstName, lastName, password, role) VALUES (?, ?, ?, ?, ?)";
        jdbcTemplate.update(sql, email, firstName, lastName, password, role);
        return login(email, password);
    }

    public List<User> getAllUsers() {
        String sql = "SELECT * FROM users";
        List<User> users = jdbcTemplate.query(sql, RowMappers.getUserRowMapper());
        return users.isEmpty() ? null : users;
    }

    public List<User> getSoleTraders(String service) {
        if (service == null || service.isEmpty()) {
            String sql = "SELECT * FROM users WHERE role = 'soleTrader'";
            List<User> users = jdbcTemplate.query(sql, RowMappers.getUserRowMapper());
            return users.isEmpty() ? null : users;
        } else {
            String sql = "SELECT * FROM users WHERE role = 'soleTrader' AND serviceOffered = ?";
            List<User> users = jdbcTemplate.query(sql, RowMappers.getUserRowMapper(), service);
            return users.isEmpty() ? null : users;
        }
    }
}