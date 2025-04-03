
package server.service;

import org.springframework.stereotype.Service;
import server.middleware.RowMappers;
import server.models.Rating;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.jdbc.core.JdbcTemplate;
import java.util.List;

@Service
public class RatingService {

    @Autowired
    private JdbcTemplate jdbcTemplate;

    public void rateUser(Integer userTo, Integer rating, Integer userFrom) {
        String sql = "INSERT INTO ratings (userTo, rating, userFrom) VALUES (?, ?, ?)";
        jdbcTemplate.update(sql, userTo, rating, userFrom);
    }

    public List<Rating> getRatingsForUser(Integer userId) {
        String sql = "SELECT * FROM ratings WHERE receiverId = ?";
        List<Rating> ratings = jdbcTemplate.query(sql, RowMappers.getRatingRowMapper(), userId);
        return ratings.isEmpty() ? null : ratings;
    }
}
