Here is a draft you can adapt for your report.md. This is the kind of reasoning your instructor is looking for.

    1. Justification of NoSQL Model Choice: Document Store (MongoDB)

    For the seasonal rentals dataset, I have chosen a Document Store model, to be implemented using MongoDB. This decision is based on a careful analysis of the data structure, the required analytical queries, and scalability considerations.

    a. Alignment with Data Structure:
    The dataset's core entity is a "listing," which is a self-contained object with numerous attributes of varying types (text, numbers, booleans, dates, and lists like amenities). This semi-structured nature maps directly and intuitively to a JSON-like document in MongoDB. Each row in the CSV can be transformed into a single document, preserving its structure and hierarchy.

    b. Optimized for Query Patterns:
    The required analytical queries involve filtering, aggregation, and sorting based on various attributes of a listing. For example:

        Count listings by property_type

        Find listings with a specific host

        Sort listings by number_of_reviews

    A document model is highly efficient for these read-heavy, query-centric workloads. By embedding related data (like host information) within the listing document itself, we can retrieve all necessary information for a query in a single database operation, eliminating the need for expensive JOIN operations that are characteristic of relational databases.

    c. Scalability and Flexibility:
    MongoDB's schema-on-read flexibility is a significant advantage. If future data scrapes include new fields, they can be added to new documents without altering existing ones. Furthermore, MongoDB is designed for horizontal scaling (sharding), which means it can handle a massive increase in data volume by distributing the load across multiple servers, a key requirement for modern, large-scale applications.

    In contrast, a Key-Value store like Redis would be too simplistic for the required queries, and a Column-Family store like HBase would introduce unnecessary complexity for this use case. The document model provides the best balance of performance, flexibility, and intuitive data modeling for this project.


schema
    {
  "_id": 80260, // We'll use the original 'id' as the primary key
  "listing_url": "https://www.airbnb.com/rooms/80260",
  "scraped_at": "2024-06-13T00:00:00Z", // Converted to proper ISODate
  "name": "Nice studio in Jourdain's village",
  "description": "...",
  "property_type": "Entire rental unit",
  "room_type": "Entire home/apt",
  "accommodates": 3,
  "bathrooms": 1.0,
  "bedrooms": 1,
  "beds": 1,
  "amenities": [
    "Hangers",
    "Essentials",
    "Wifi",
    "Dishes and silverware",
    "Dedicated workspace",
    "Hair dryer",
    "Kitchen",
    "Shampoo",
    "Pets allowed",
    "Heating"
  ],
  "price": 150.00, // Cleaned to be a numeric type
  "minimum_nights": 2,
  "maximum_nights": 730,
  "instant_bookable": false,

  "host": {
    "id": 333548,
    "name": "Charlotte",
    "since": "2011-01-03T00:00:00Z", // Converted to ISODate
    "location": "Paris, France",
    "about": "My name is Charlotte...",
    "is_superhost": false,
    "listings_count": 1,
    "has_profile_pic": true,
    "is_identity_verified": true
  },

  "location": {
    "address": "Ménilmontant, Paris, Île-de-France, France", // Maybe combine fields
    "neighbourhood_cleansed": "Ménilmontant",
    "coordinates": {
      "type": "Point",
      "coordinates": [ 2.38848, 48.87131 ] // [longitude, latitude] for GeoJSON
    }
  },

  "reviews": {
    "count": 206,
    "score_rating": 4.63,
    "score_accuracy": 4.61,
    "score_cleanliness": 4.75,
    "score_checkin": 4.85,
    "score_communication": 4.78,
    "score_location": 4.61,
    "score_value": 4.64,
    "first_review_date": "2011-04-18T00:00:00Z", // ISODate
    "last_review_date": "2021-10-03T00:00:00Z" // ISODate
  },

  "availability": {
    "has_availability": true,
    "availability_30": 0,
    "availability_90": 0,
    "availability_365": 0
  }
}