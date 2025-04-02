package server.middleware;

import server.models.User;
import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Component;

@Component
public class Request {
    
    @Autowired
    private JdbcTemplate jdbcTemplate;

    public User getUserFromToken(String userToken) {
        
        // Assuming userToken is the userId
        var userId = Integer.parseInt(userToken);


        String sql = "SELECT * FROM users WHERE userId = ?";
        List<User> users = jdbcTemplate.query(sql, RowMappers.getUserRowMapper(), userId);

        if (users.isEmpty()) {
            return null;
        }

        User user = users.get(0);
        
        return user;
    }
}
