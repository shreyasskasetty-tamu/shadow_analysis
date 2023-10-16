# Shadow Analysis API Documentation

## Overview

The Shadow Analysis API is a service for performing shadow calculations on Digital Surface Model (DSM) data. This API allows you to calculate shadows based on provided azimuth, altitude, DSM, and scale parameters. Additionally, you can retrieve shadow analysis results using a unique document ID.

## Base URL

The base URL for all API endpoints is:

`ec2-35-173-183-116.compute-1.amazonaws.com:5001/api/v1/shadow_analysis/`

## Endpoints

### 1. Test Endpoint

#### GET `/test`

This endpoint can be used to check if the service is up and running.

**Request:**

```http
GET /api/v1/shadow_analysis/test
```

**Response:**
`200 OK`: Service is running successfully.

### 2. Calculate Shadow Endpoint
#### POST `/calculate-shadow`
**Request:**
```http
POST /api/v1/shadow_analysis/calculate-shadow
```
This endpoint allows you to calculate shadows based on the provided parameters and store the results in MongoDB.

**Headers:**

`Content-Type: application/json`

**JSON Body:**
```
{
  "azimuth": 180,
  "altitude": 45,
  "dsm": [[], []], // 2D array representing DSM data
  "scale": 0.1
}
```
**Response:**

`200 OK`: Returns the document ID of stored MongoDB Document. Shadow analysis completed successfully, and the results are stored in MongoDB.

**Example Response:**
```
{
    "id": "fc6bf79f-24d9-494f-80ae-0abf5960a1f1",
    "message": "Shadow analysis completed and stored in MongoDB"
}
```

`400 Bad Request`: Missing required data in the request.
**Example Response:**
```
{
  "error": "Missing required data"
}
```

`500 Internal Server Error`: An error occurred during shadow analysis.

**Example Response:**
```
{
  error": "An error occurred during shadow analysis"
}
```

### 3. Calculate Shadow Endpoint
#### POST `/get-shadow-data`
**Request:**
```http
POST /api/v1/shadow_analysis/get-shadow-data
```
This endpoint allows you to retrieve shadow analysis results based on a provided document ID.

**Headers:**
`Content-Type: application/json`

**Response:**

`200 OK`: Shadow data retrieved successfully.

**Example Response:**
```
{
  "shadow_data": {
    "_id": "fc6bf79f-24d9-494f-80ae-0abf5960a1f1",
    "sh": [], // Shadow data
    "timestamp": "2023-10-16T12:34:56.789Z"
  }
}
```

`400 Bad Request`: Missing document ID in the request.
**Example Response:**
```
{
  "error": "Missing document_id in request"
}
```

`404 Not Found`: Document not found for the provided document ID.
**Example Response:**
```
{
  "error": "Document not found"
}
```