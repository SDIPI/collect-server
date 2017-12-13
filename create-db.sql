-- phpMyAdmin SQL Dump
-- version 4.6.6deb4
-- https://www.phpmyadmin.net/
--
-- Client :  localhost:3306
-- Généré le :  Mer 13 Décembre 2017 à 20:26
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
  `wdfId` varchar(64) NOT NULL,
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
-- Structure de la table `event`
--

CREATE TABLE `event` (
  `wdfId` varchar(64) NOT NULL,
  `url` varchar(512) NOT NULL,
  `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `type` varchar(32) NOT NULL,
  `value` varchar(512) DEFAULT NULL,
  `id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Structure de la table `interests`
--

CREATE TABLE `interests` (
  `id` int(11) NOT NULL,
  `name` varchar(96) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Contenu de la table `interests`
--

INSERT INTO `interests` (`id`, `name`) VALUES
(1, 'Banking & Finance / Avid Investor'),
(2, 'Beauty & Wellness / Beauty Maven'),
(3, 'Food & Dining / Cooking Enthusiast'),
(4, 'Food & Dining / Cooking Enthusiast / 30 Minute Chef'),
(5, 'Food & Dining / Cooking Enthusiast / Aspiring Chef'),
(6, 'Food & Dining / Fast Food Craver'),
(7, 'Food & Dining / Foodie'),
(8, 'Home & Garden / Do-It-Yourselfer'),
(9, 'Home & Garden / Home Decor Enthusiast'),
(10, 'Lifestyles & Hobbies / Art & Theater Aficionado'),
(11, 'Lifestyles & Hobbies / Business Professional'),
(12, 'Lifestyles & Hobbies / Family-Focused'),
(13, 'Lifestyles & Hobbies / Fashionista'),
(14, 'Lifestyles & Hobbies / Green Living Enthusiast'),
(15, 'Lifestyles & Hobbies / Nightlife Enthusiast'),
(16, 'Lifestyles & Hobbies / Outdoor Enthusiast'),
(17, 'Lifestyles & Hobbies / Pet Lover'),
(18, 'Lifestyles & Hobbies / Pet Lover / Cat Lover'),
(19, 'Lifestyles & Hobbies / Pet Lover / Dog Lover'),
(20, 'Lifestyles & Hobbies / Shutterbug'),
(21, 'Lifestyles & Hobbies / Thrill Seeker'),
(22, 'Media & Entertainment / Book Lover'),
(23, 'Media & Entertainment / Comics & Animation Fan'),
(24, 'Media & Entertainment / Gamer'),
(25, 'Media & Entertainment / Gamer / Action Game Fan'),
(26, 'Media & Entertainment / Gamer / Adventure & Strategy Game Fan'),
(27, 'Media & Entertainment / Gamer / Casual & Social Gamer'),
(28, 'Media & Entertainment / Gamer / Driving & Racing Game Fan'),
(29, 'Media & Entertainment / Gamer / Hardcore Gamer'),
(30, 'Media & Entertainment / Gamer / Roleplaying Game Fan'),
(31, 'Media & Entertainment / Gamer / Shooter Game Fan'),
(32, 'Media & Entertainment / Gamer / Sports Game Fan'),
(33, 'Media & Entertainment / Movie Lover'),
(34, 'Media & Entertainment / Movie Lover / Action & Adventure Movie Fan'),
(35, 'Media & Entertainment / Movie Lover / Comedy Movie Fan'),
(36, 'Media & Entertainment / Movie Lover / Family Movie Fan'),
(37, 'Media & Entertainment / Movie Lover / Horror Movie Fan'),
(38, 'Media & Entertainment / Movie Lover / Romance & Drama Movie Fan'),
(39, 'Media & Entertainment / Movie Lover / Sci-Fi & Fantasy Movie Fan'),
(40, 'Media & Entertainment / Movie Lover / South Asian Film Fan'),
(41, 'Media & Entertainment / Music Lover'),
(42, 'Media & Entertainment / Music Lover / Blues Fan'),
(43, 'Media & Entertainment / Music Lover / Classical Music Enthusiast'),
(44, 'Media & Entertainment / Music Lover / Country Music Fan'),
(45, 'Media & Entertainment / Music Lover / Electronica & Dance Music Fan'),
(46, 'Media & Entertainment / Music Lover / Folk & Traditional Music Enthusiast'),
(47, 'Media & Entertainment / Music Lover / Indie & Alternative Rock Fan'),
(48, 'Media & Entertainment / Music Lover / Jazz Enthusiast'),
(49, 'Media & Entertainment / Music Lover / Metalhead'),
(50, 'Media & Entertainment / Music Lover / Pop Music Fan'),
(51, 'Media & Entertainment / Music Lover / Rap & Hip Hop Fan'),
(52, 'Media & Entertainment / Music Lover / Rock Music Fan'),
(53, 'Media & Entertainment / Music Lover / Spanish-Language Music Fan'),
(54, 'Media & Entertainment / Music Lover / World Music Fan'),
(55, 'Media & Entertainment / TV Lover'),
(56, 'Media & Entertainment / TV Lover / Family Television Fan'),
(57, 'Media & Entertainment / TV Lover / Game, Reality & Talk Show Fan'),
(58, 'Media & Entertainment / TV Lover / Sci-Fi & Fantasy TV Fan'),
(59, 'Media & Entertainment / TV Lover / TV Comedy Fan'),
(60, 'Media & Entertainment / TV Lover / TV Drama Fan'),
(61, 'News & Politics / News Junkie'),
(62, 'News & Politics / News Junkie / Business & Economic News Junkie'),
(63, 'News & Politics / News Junkie / Entertainment & Celebrity News Junkie'),
(64, 'News & Politics / News Junkie / Local News Junkie'),
(65, 'News & Politics / News Junkie / Political News Junkie'),
(66, 'News & Politics / News Junkie / Women\'s Media Fan'),
(67, 'News & Politics / News Junkie / World News Junkie'),
(68, 'Shoppers / Bargain Hunter'),
(69, 'Shoppers / Luxury Shopper'),
(70, 'Shoppers / Shopaholic'),
(71, 'Shoppers / Value Shopper'),
(72, 'Sports & Fitness / Health & Fitness Buff'),
(73, 'Sports & Fitness / Sports Fan'),
(74, 'Sports & Fitness / Sports Fan / American Football Fan'),
(75, 'Sports & Fitness / Sports Fan / Australian Football Fan'),
(76, 'Sports & Fitness / Sports Fan / Baseball Fan'),
(77, 'Sports & Fitness / Sports Fan / Basketball Fan'),
(78, 'Sports & Fitness / Sports Fan / Boating & Sailing Enthusiast'),
(79, 'Sports & Fitness / Sports Fan / Cricket Enthusiast'),
(80, 'Sports & Fitness / Sports Fan / Cycling Enthusiast'),
(81, 'Sports & Fitness / Sports Fan / Fight & Wrestling Fan'),
(82, 'Sports & Fitness / Sports Fan / Golf Enthusiast'),
(83, 'Sports & Fitness / Sports Fan / Hockey Fan'),
(84, 'Sports & Fitness / Sports Fan / Motor Sports Enthusiast'),
(85, 'Sports & Fitness / Sports Fan / Racquetball Enthusiast'),
(86, 'Sports & Fitness / Sports Fan / Rugby Enthusiast'),
(87, 'Sports & Fitness / Sports Fan / Running Enthusiast'),
(88, 'Sports & Fitness / Sports Fan / Soccer Fan'),
(89, 'Sports & Fitness / Sports Fan / Tennis Enthusiast'),
(90, 'Sports & Fitness / Sports Fan / Water Sports Enthusiast'),
(91, 'Technology / Mobile Enthusiast'),
(92, 'Technology / Social Media Enthusiast'),
(93, 'Technology / Technophile'),
(94, 'Travel / Business Traveler'),
(95, 'Travel / Travel Buff'),
(96, 'Travel / Travel Buff / Beachbound Traveler'),
(97, 'Travel / Travel Buff / Family Vacationer'),
(98, 'Travel / Travel Buff / Luxury Traveler'),
(99, 'Vehicles & Transportation / Auto Enthusiast'),
(100, 'Vehicles & Transportation / Auto Enthusiast / Motorcycle Enthusiast'),
(101, 'Vehicles & Transportation / Auto Enthusiast / Performance & Luxury Vehicle Enthusiast'),
(102, 'Vehicles & Transportation / Auto Enthusiast / Truck & SUV Enthusiast');

-- --------------------------------------------------------

--
-- Structure de la table `pagerequests`
--

CREATE TABLE `pagerequests` (
  `wdfId` varchar(64) NOT NULL,
  `url` varchar(1024) NOT NULL,
  `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `request` varchar(2048) NOT NULL,
  `method` varchar(8) NOT NULL,
  `id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Structure de la table `pageviews`
--

CREATE TABLE `pageviews` (
  `wdfId` varchar(64) NOT NULL,
  `url` varchar(1024) NOT NULL,
  `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Structure de la table `pagewatch`
--

CREATE TABLE `pagewatch` (
  `wdfId` varchar(64) NOT NULL,
  `url` varchar(512) NOT NULL,
  `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `amount` int(11) NOT NULL,
  `id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Structure de la table `users`
--

CREATE TABLE `users` (
  `wdfId` int(11) NOT NULL,
  `wdfToken` varchar(64) DEFAULT NULL,
  `facebookId` bigint(20) NOT NULL,
  `facebookAccessToken` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Index pour les tables exportées
--

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
  ADD PRIMARY KEY (`id`);

--
-- Index pour la table `content_text`
--
ALTER TABLE `content_text`
  ADD PRIMARY KEY (`url`);

--
-- Index pour la table `event`
--
ALTER TABLE `event`
  ADD PRIMARY KEY (`id`);

--
-- Index pour la table `interests`
--
ALTER TABLE `interests`
  ADD PRIMARY KEY (`id`);

--
-- Index pour la table `pagerequests`
--
ALTER TABLE `pagerequests`
  ADD PRIMARY KEY (`id`);

--
-- Index pour la table `pageviews`
--
ALTER TABLE `pageviews`
  ADD PRIMARY KEY (`wdfId`,`url`,`timestamp`);

--
-- Index pour la table `pagewatch`
--
ALTER TABLE `pagewatch`
  ADD PRIMARY KEY (`id`);

--
-- Index pour la table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`wdfId`),
  ADD UNIQUE KEY `facebookId` (`facebookId`),
  ADD KEY `wdfIf` (`wdfId`),
  ADD KEY `facebookId_2` (`facebookId`);

--
-- AUTO_INCREMENT pour les tables exportées
--

--
-- AUTO_INCREMENT pour la table `content`
--
ALTER TABLE `content`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=1024;
--
-- AUTO_INCREMENT pour la table `event`
--
ALTER TABLE `event`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=872;
--
-- AUTO_INCREMENT pour la table `interests`
--
ALTER TABLE `interests`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=103;
--
-- AUTO_INCREMENT pour la table `pagerequests`
--
ALTER TABLE `pagerequests`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=198675;
--
-- AUTO_INCREMENT pour la table `pagewatch`
--
ALTER TABLE `pagewatch`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7181;
--
-- AUTO_INCREMENT pour la table `users`
--
ALTER TABLE `users`
  MODIFY `wdfId` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=31;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
