-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: bkszc7akpfonprqakjbk-mysql.services.clever-cloud.com:3306
-- Tiempo de generación: 22-11-2024 a las 16:08:21
-- Versión del servidor: 8.0.15-5
-- Versión de PHP: 8.2.21

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `bkszc7akpfonprqakjbk`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `fechas`
--

CREATE TABLE `fechas` (
  `id_fecha` int(11) NOT NULL,
  `fecha` date NOT NULL,
  `dia` int(11) NOT NULL,
  `mes` int(11) NOT NULL,
  `anio` int(11) NOT NULL,
  `feriado` tinyint(1) DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `mov_subte`
--

CREATE TABLE `mov_subte` (
  `id_subte` int(11) NOT NULL,
  `id_fecha` int(11) NOT NULL,
  `hora` varchar(20) DEFAULT NULL,
  `turno` varchar(50) NOT NULL,
  `cantidad` double NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `mov_vehiculo`
--

CREATE TABLE `mov_vehiculo` (
  `id_ubicacion` int(11) NOT NULL,
  `id_fecha` int(11) NOT NULL,
  `hora` varchar(20) NOT NULL,
  `cantidad` decimal(10,0) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `subte`
--

CREATE TABLE `subte` (
  `id_subte` int(11) NOT NULL,
  `id_ubicacion` int(11) NOT NULL,
  `linea` varchar(20) NOT NULL,
  `estacion` varchar(50) DEFAULT NULL,
  `molinete` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `ubicacion`
--

CREATE TABLE `ubicacion` (
  `id_ubicacion` int(11) NOT NULL,
  `latitud` varchar(50) NOT NULL,
  `longitud` varchar(50) NOT NULL,
  `geohash` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `fechas`
--
ALTER TABLE `fechas`
  ADD PRIMARY KEY (`id_fecha`),
  ADD UNIQUE KEY `UK_FECHA` (`fecha`);

--
-- Indices de la tabla `mov_subte`
--
ALTER TABLE `mov_subte`
  ADD KEY `id_fecha` (`id_fecha`),
  ADD KEY `id_subte` (`id_subte`);

--
-- Indices de la tabla `mov_vehiculo`
--
ALTER TABLE `mov_vehiculo`
  ADD KEY `FK_UBICACION_2` (`id_ubicacion`),
  ADD KEY `id_fecha` (`id_fecha`);

--
-- Indices de la tabla `subte`
--
ALTER TABLE `subte`
  ADD PRIMARY KEY (`id_subte`),
  ADD KEY `FK_UBICACION` (`id_ubicacion`);

--
-- Indices de la tabla `ubicacion`
--
ALTER TABLE `ubicacion`
  ADD PRIMARY KEY (`id_ubicacion`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `fechas`
--
ALTER TABLE `fechas`
  MODIFY `id_fecha` int(11) NOT NULL AUTO_INCREMENT;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `mov_subte`
--
ALTER TABLE `mov_subte`
  ADD CONSTRAINT `FK_SUBTE` FOREIGN KEY (`id_subte`) REFERENCES `subte` (`id_subte`),
  ADD CONSTRAINT `mov_subte_ibfk_1` FOREIGN KEY (`id_fecha`) REFERENCES `fechas` (`id_fecha`);

--
-- Filtros para la tabla `mov_vehiculo`
--
ALTER TABLE `mov_vehiculo`
  ADD CONSTRAINT `FK_UBICACION_2` FOREIGN KEY (`id_ubicacion`) REFERENCES `ubicacion` (`id_ubicacion`),
  ADD CONSTRAINT `mov_vehiculo_ibfk_1` FOREIGN KEY (`id_fecha`) REFERENCES `fechas` (`id_fecha`);

--
-- Filtros para la tabla `subte`
--
ALTER TABLE `subte`
  ADD CONSTRAINT `FK_UBICACION` FOREIGN KEY (`id_ubicacion`) REFERENCES `ubicacion` (`id_ubicacion`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
