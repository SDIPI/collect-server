-- phpMyAdmin SQL Dump
-- version 4.6.6deb4
-- https://www.phpmyadmin.net/
--
-- Client :  localhost:3306
-- Généré le :  Mar 30 Janvier 2018 à 15:14
-- Version du serveur :  5.7.20-0ubuntu0.17.04.1
-- Version de PHP :  7.0.22-0ubuntu0.17.04.1

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de données :  `wdf`
--

-- --------------------------------------------------------

--
-- Structure de la table `computed_bestwords`
--

CREATE TABLE `computed_bestwords` (
  `url` varchar(1024) NOT NULL,
  `word` varchar(256) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `tfidf` float NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Structure de la table `computed_df`
--

CREATE TABLE `computed_df` (
  `word` varchar(256) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `df` int(10) UNSIGNED NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Structure de la table `computed_tf`
--

CREATE TABLE `computed_tf` (
  `url` varchar(1024) NOT NULL,
  `word` varchar(256) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `tf` int(10) UNSIGNED NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Structure de la table `computed_tfidf`
--

CREATE TABLE `computed_tfidf` (
  `url` varchar(1024) NOT NULL,
  `word` varchar(256) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `tfidf` float NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Structure de la table `content`
--

CREATE TABLE `content` (
  `id` int(11) NOT NULL,
  `wdfId` int(11) NOT NULL,
  `url` varchar(1024) NOT NULL,
  `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `content` mediumtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `language` varchar(8) DEFAULT NULL,
  `title` varchar(512) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Structure de la table `content_text`
--

CREATE TABLE `content_text` (
  `url` varchar(1024) NOT NULL,
  `content` mediumtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `title` varchar(512) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `language` varchar(8) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Structure de la table `current_url_topics`
--

CREATE TABLE `current_url_topics` (
  `url` varchar(1024) NOT NULL,
  `topic` int(11) NOT NULL,
  `probability` float NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Structure de la table `current_user_tags`
--

CREATE TABLE `current_user_tags` (
  `wdfId` int(11) NOT NULL,
  `topic_id` int(11) NOT NULL,
  `interest_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Structure de la table `interests`
--

CREATE TABLE `interests` (
  `id` int(11) NOT NULL,
  `name` varchar(96) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Structure de la table `lda_topics`
--

CREATE TABLE `lda_topics` (
  `topic_id` int(11) NOT NULL,
  `word` varchar(256) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `value` float NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Structure de la table `pagerequests`
--

CREATE TABLE `pagerequests` (
  `wdfId` int(11) NOT NULL,
  `url` varchar(1024) NOT NULL,
  `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `request` varchar(2048) NOT NULL,
  `method` varchar(8) NOT NULL,
  `size` int(10) UNSIGNED DEFAULT NULL,
  `id` int(11) NOT NULL,
  `urlDomain` varchar(1024) DEFAULT NULL,
  `requestDomain` varchar(1024) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Structure de la table `pageviews`
--

CREATE TABLE `pageviews` (
  `wdfId` int(11) NOT NULL,
  `url` varchar(1024) NOT NULL,
  `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Structure de la table `pagewatch`
--

CREATE TABLE `pagewatch` (
  `wdfId` int(11) NOT NULL,
  `url` varchar(512) NOT NULL,
  `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `amount` int(11) NOT NULL,
  `id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Structure de la table `precalc_topics`
--

CREATE TABLE `precalc_topics` (
  `url` varchar(1024) NOT NULL,
  `topics` varchar(4096) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Structure de la table `precalc_trackers`
--

CREATE TABLE `precalc_trackers` (
  `wdfId` int(11) NOT NULL,
  `urlDomain` varchar(400) NOT NULL,
  `reqDomain` varchar(400) NOT NULL,
  `amount` int(11) NOT NULL,
  `size` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Structure de la table `users`
--

CREATE TABLE `users` (
  `wdfId` int(11) NOT NULL,
  `wdfToken` varchar(64) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Structure de la table `user_interests`
--

CREATE TABLE `user_interests` (
  `wdfId` int(11) NOT NULL,
  `interest_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Structure de la table `user_tags`
--

CREATE TABLE `user_tags` (
  `wdfId` int(11) NOT NULL,
  `interest_id` int(11) NOT NULL,
  `word` varchar(256) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Index pour les tables exportées
--

--
-- Index pour la table `computed_bestwords`
--
ALTER TABLE `computed_bestwords`
  ADD PRIMARY KEY (`url`,`word`);

--
-- Index pour la table `computed_df`
--
ALTER TABLE `computed_df`
  ADD PRIMARY KEY (`word`);

--
-- Index pour la table `computed_tf`
--
ALTER TABLE `computed_tf`
  ADD PRIMARY KEY (`url`,`word`);

--
-- Index pour la table `computed_tfidf`
--
ALTER TABLE `computed_tfidf`
  ADD PRIMARY KEY (`url`,`word`);

--
-- Index pour la table `content`
--
ALTER TABLE `content`
  ADD PRIMARY KEY (`id`),
  ADD KEY `wdfId` (`wdfId`),
  ADD KEY `url` (`url`);

--
-- Index pour la table `content_text`
--
ALTER TABLE `content_text`
  ADD PRIMARY KEY (`url`);

--
-- Index pour la table `current_url_topics`
--
ALTER TABLE `current_url_topics`
  ADD PRIMARY KEY (`url`,`topic`);

--
-- Index pour la table `current_user_tags`
--
ALTER TABLE `current_user_tags`
  ADD PRIMARY KEY (`wdfId`,`topic_id`);

--
-- Index pour la table `interests`
--
ALTER TABLE `interests`
  ADD PRIMARY KEY (`id`);

--
-- Index pour la table `lda_topics`
--
ALTER TABLE `lda_topics`
  ADD PRIMARY KEY (`topic_id`,`word`);

--
-- Index pour la table `pagerequests`
--
ALTER TABLE `pagerequests`
  ADD PRIMARY KEY (`id`),
  ADD KEY `urlDomain` (`urlDomain`),
  ADD KEY `requestDomain` (`requestDomain`),
  ADD KEY `wdfId` (`wdfId`),
  ADD KEY `wdfId_2` (`wdfId`),
  ADD KEY `wdfId_3` (`wdfId`);

--
-- Index pour la table `pageviews`
--
ALTER TABLE `pageviews`
  ADD PRIMARY KEY (`wdfId`,`url`,`timestamp`),
  ADD KEY `wdfId` (`wdfId`);

--
-- Index pour la table `pagewatch`
--
ALTER TABLE `pagewatch`
  ADD PRIMARY KEY (`id`),
  ADD KEY `wdfId` (`wdfId`);

--
-- Index pour la table `precalc_topics`
--
ALTER TABLE `precalc_topics`
  ADD PRIMARY KEY (`url`);

--
-- Index pour la table `precalc_trackers`
--
ALTER TABLE `precalc_trackers`
  ADD PRIMARY KEY (`wdfId`,`urlDomain`,`reqDomain`),
  ADD KEY `wdfId` (`wdfId`);

--
-- Index pour la table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`wdfId`),
  ADD KEY `wdfIf` (`wdfId`);

--
-- Index pour la table `user_interests`
--
ALTER TABLE `user_interests`
  ADD PRIMARY KEY (`wdfId`,`interest_id`),
  ADD KEY `interest_id` (`interest_id`);

--
-- Index pour la table `user_tags`
--
ALTER TABLE `user_tags`
  ADD PRIMARY KEY (`wdfId`,`interest_id`,`word`);

--
-- AUTO_INCREMENT pour les tables exportées
--

--
-- AUTO_INCREMENT pour la table `content`
--
ALTER TABLE `content`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9853;
--
-- AUTO_INCREMENT pour la table `interests`
--
ALTER TABLE `interests`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=103;
--
-- AUTO_INCREMENT pour la table `pagerequests`
--
ALTER TABLE `pagerequests`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2912459;
--
-- AUTO_INCREMENT pour la table `pagewatch`
--
ALTER TABLE `pagewatch`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=86978;
--
-- AUTO_INCREMENT pour la table `users`
--
ALTER TABLE `users`
  MODIFY `wdfId` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=164;
--
-- Contraintes pour les tables exportées
--

--
-- Contraintes pour la table `content`
--
ALTER TABLE `content`
  ADD CONSTRAINT `content_ibfk_1` FOREIGN KEY (`wdfId`) REFERENCES `users` (`wdfId`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Contraintes pour la table `content_text`
--
ALTER TABLE `content_text`
  ADD CONSTRAINT `content_text_ibfk_1` FOREIGN KEY (`url`) REFERENCES `content` (`url`);

--
-- Contraintes pour la table `current_user_tags`
--
ALTER TABLE `current_user_tags`
  ADD CONSTRAINT `current_user_tags_ibfk_1` FOREIGN KEY (`wdfId`) REFERENCES `users` (`wdfId`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Contraintes pour la table `pagerequests`
--
ALTER TABLE `pagerequests`
  ADD CONSTRAINT `pagerequests_ibfk_1` FOREIGN KEY (`wdfId`) REFERENCES `users` (`wdfId`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Contraintes pour la table `pageviews`
--
ALTER TABLE `pageviews`
  ADD CONSTRAINT `pageviews_ibfk_1` FOREIGN KEY (`wdfId`) REFERENCES `users` (`wdfId`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Contraintes pour la table `pagewatch`
--
ALTER TABLE `pagewatch`
  ADD CONSTRAINT `pagewatch_ibfk_1` FOREIGN KEY (`wdfId`) REFERENCES `users` (`wdfId`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Contraintes pour la table `precalc_trackers`
--
ALTER TABLE `precalc_trackers`
  ADD CONSTRAINT `precalc_trackers_ibfk_1` FOREIGN KEY (`wdfId`) REFERENCES `users` (`wdfId`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Contraintes pour la table `user_interests`
--
ALTER TABLE `user_interests`
  ADD CONSTRAINT `user_interests_ibfk_1` FOREIGN KEY (`wdfId`) REFERENCES `users` (`wdfId`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `user_interests_ibfk_2` FOREIGN KEY (`interest_id`) REFERENCES `interests` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Contraintes pour la table `user_tags`
--
ALTER TABLE `user_tags`
  ADD CONSTRAINT `user_tags_ibfk_1` FOREIGN KEY (`wdfId`) REFERENCES `users` (`wdfId`) ON DELETE CASCADE ON UPDATE CASCADE;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
