CREATE DEFINER = CURRENT_USER PROCEDURE `update_df`(IN url_p  VARCHAR(1024)
                                                              CHARSET latin1,
                                                    IN word_p VARCHAR(256)
                                                              CHARSET utf8mb4
                                                              COLLATE utf8mb4_unicode_ci)
  BEGIN
    IF NOT (SELECT count(*)
            FROM wdf.computed_tf
            WHERE `url` = url_p AND `word` = word_p) > 0
    THEN
      BEGIN
        IF (SELECT count(*)
            FROM wdf.computed_df
            WHERE `word` = word_p)
        THEN BEGIN
          UPDATE wdf.computed_df
          SET `df` = `df` + 1
          WHERE `word` = word_p;
        END;
        ELSE BEGIN
          INSERT INTO wdf.computed_df (`word`, `df`)
          VALUES (word_p, 1);
        END;
        END IF;
      END;
    END IF;
  END;


CREATE DEFINER = CURRENT_USER PROCEDURE `update_tfidf`(IN url_p  VARCHAR(1024)
                                                                 CHARSET latin1,
                                                       IN word_p VARCHAR(256)
                                                                 CHARSET utf8mb4
                                                                 COLLATE utf8mb4_unicode_ci)
  BEGIN
    SET @documents = (SELECT COUNT(DISTINCT url)
                      FROM `computed_tf`);
    INSERT INTO computed_tfidf (url, word, tfidf)
      SELECT (url_p, word_p, `computed_tf`.tf * LOG(@documents / `computed_df`.df))
      FROM `computed_tf`, `computed_df`
    ON DUPLICATE KEY UPDATE tfidf = `computed_tf`.tf * LOG(@documents / `computed_df`.df);

  END;
