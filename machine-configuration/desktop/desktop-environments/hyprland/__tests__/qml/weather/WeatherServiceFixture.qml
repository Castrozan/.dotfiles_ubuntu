import QtQuick

Item {
    id: root

    property QtObject weatherServiceLogic: QtObject {
        id: weatherServiceLogic

        property string locationCoordinates: ""

        readonly property var weatherIconMap: ({
                "0": "clear_day",
                "1": "clear_day",
                "2": "partly_cloudy_day",
                "3": "cloud",
                "45": "foggy",
                "48": "foggy",
                "51": "rainy",
                "53": "rainy",
                "55": "rainy",
                "56": "rainy",
                "57": "rainy",
                "61": "rainy",
                "63": "rainy",
                "65": "rainy",
                "66": "rainy",
                "67": "rainy",
                "71": "cloudy_snowing",
                "73": "cloudy_snowing",
                "75": "snowing_heavy",
                "77": "cloudy_snowing",
                "80": "rainy",
                "81": "rainy",
                "82": "rainy",
                "85": "cloudy_snowing",
                "86": "snowing_heavy",
                "95": "thunderstorm",
                "96": "thunderstorm",
                "99": "thunderstorm"
            })

        readonly property var weatherConditionMap: ({
                "0": "Clear",
                "1": "Clear",
                "2": "Partly cloudy",
                "3": "Overcast",
                "45": "Fog",
                "48": "Fog",
                "51": "Drizzle",
                "53": "Drizzle",
                "55": "Drizzle",
                "56": "Freezing drizzle",
                "57": "Freezing drizzle",
                "61": "Light rain",
                "63": "Rain",
                "65": "Heavy rain",
                "66": "Light rain",
                "67": "Heavy rain",
                "71": "Light snow",
                "73": "Snow",
                "75": "Heavy snow",
                "77": "Snow",
                "80": "Light rain",
                "81": "Rain",
                "82": "Heavy rain",
                "85": "Light snow showers",
                "86": "Heavy snow showers",
                "95": "Thunderstorm",
                "96": "Thunderstorm with hail",
                "99": "Thunderstorm with hail"
            })

        function getWeatherIcon(code) {
            if (weatherIconMap.hasOwnProperty(code))
                return weatherIconMap[code];
            return "air";
        }

        function getWeatherCondition(code) {
            return weatherConditionMap[code] || "Unknown";
        }

        function celsiusToFahrenheit(celsius) {
            return celsius * 9 / 5 + 32;
        }

        function buildWeatherApiUrl() {
            if (!locationCoordinates || locationCoordinates.indexOf(",") === -1)
                return "";

            var parts = locationCoordinates.split(",");
            var latitude = parts[0];
            var longitude = parts[1];
            var baseUrl = "https://api.open-meteo.com/v1/forecast";
            var queryParams = ["latitude=" + latitude, "longitude=" + longitude, "daily=weather_code,temperature_2m_max,temperature_2m_min,sunrise,sunset", "current=temperature_2m,relative_humidity_2m,apparent_temperature,is_day,weather_code,wind_speed_10m", "timezone=auto", "forecast_days=7"];

            return baseUrl + "?" + queryParams.join("&");
        }

        property var currentConditions: null
        property var forecast: []

        function parseWeatherResponse(responseText) {
            var json = JSON.parse(responseText);
            if (!json.current || !json.daily)
                return;

            currentConditions = {
                weatherCode: json.current.weather_code,
                weatherDesc: getWeatherCondition(json.current.weather_code),
                tempC: Math.round(json.current.temperature_2m),
                tempF: Math.round(celsiusToFahrenheit(json.current.temperature_2m)),
                feelsLikeC: Math.round(json.current.apparent_temperature),
                feelsLikeF: Math.round(celsiusToFahrenheit(json.current.apparent_temperature)),
                humidity: json.current.relative_humidity_2m,
                windSpeed: json.current.wind_speed_10m,
                isDay: json.current.is_day,
                sunrise: json.daily.sunrise[0],
                sunset: json.daily.sunset[0]
            };

            var forecastList = [];
            for (var i = 0; i < json.daily.time.length; i++)
                forecastList.push({
                    date: json.daily.time[i],
                    maxTempC: Math.round(json.daily.temperature_2m_max[i]),
                    maxTempF: Math.round(celsiusToFahrenheit(json.daily.temperature_2m_max[i])),
                    minTempC: Math.round(json.daily.temperature_2m_min[i]),
                    minTempF: Math.round(celsiusToFahrenheit(json.daily.temperature_2m_min[i])),
                    weatherCode: json.daily.weather_code[i],
                    icon: getWeatherIcon(json.daily.weather_code[i])
                });
            forecast = forecastList;
        }
    }
}
