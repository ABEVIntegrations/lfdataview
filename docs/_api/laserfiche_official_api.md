{
  "openapi": "3.0.4",
  "info": {
    "title": "Laserfiche OData API",
    "description": "Use the Laserfiche OData API to query and manage your Laserfiche lookup table data. Try out the Table API to perform row-level CRUD operations.<p><strong>Build# : </strong>13ad8ac3c30140e5c773f2135cd15f106ffce5a8_.20250825.1</p>",
    "version": "1.0"
  },
  "servers": [
    {
      "url": "https://api.laserfiche.com/odata4"
    }
  ],
  "paths": {
    "/table/$metadata": {
      "get": {
        "tags": [
          "SecureMetadata"
        ],
        "summary": "Generates the table OData $metadata document that contains column definitions for all tables.",
        "description": "- Required OAuth scope: table.Read\n- ReplaceAllRowsAsync action requires Forms File input for multipart/form-data request but this is not reflected in the metadata. Customization may be needed to use this action from generated OData client.",
        "operationId": "GetTableMetadata",
        "responses": {
          "200": {
            "description": "Table OData metadata document.",
            "content": {
              "application/xml": {
                "schema": {
                  "$ref": "#/components/schemas/TableMetadataResponse"
                }
              }
            }
          },
          "401": {
            "description": "Access token was invalid or expired.",
            "content": {
              "application/xml": {
                "schema": {
                  "$ref": "#/components/schemas/ExtendedProblemDetails"
                }
              },
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ExtendedProblemDetails"
                }
              }
            }
          },
          "403": {
            "description": "Access denied for the operation.",
            "content": {
              "application/xml": {
                "schema": {
                  "$ref": "#/components/schemas/ExtendedProblemDetails"
                }
              },
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ExtendedProblemDetails"
                }
              }
            }
          },
          "404": {
            "description": "Operation unavailable.",
            "content": {
              "application/xml": {
                "schema": {
                  "$ref": "#/components/schemas/ExtendedProblemDetails"
                }
              },
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ExtendedProblemDetails"
                }
              }
            }
          },
          "429": {
            "description": "Rate limit was reached.",
            "content": {
              "application/xml": {
                "schema": {
                  "$ref": "#/components/schemas/ExtendedProblemDetails"
                }
              },
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ExtendedProblemDetails"
                }
              }
            }
          }
        }
      }
    },
    "/table": {
      "get": {
        "tags": [
          "SecureMetadata"
        ],
        "summary": "Generates the table OData service document that lists all tables.",
        "description": "- Required OAuth scope: table.Read",
        "operationId": "GetTableODataServiceDocument",
        "responses": {
          "200": {
            "description": "Table OData service document.",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ODataServiceDocumentElementCollectionResponse"
                }
              }
            }
          },
          "401": {
            "description": "Access token was invalid or expired.",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ExtendedProblemDetails"
                }
              }
            }
          },
          "403": {
            "description": "Access denied for the operation.",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ExtendedProblemDetails"
                }
              }
            }
          },
          "404": {
            "description": "Operation unavailable.",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ExtendedProblemDetails"
                }
              }
            }
          },
          "429": {
            "description": "Rate limit was reached.",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ExtendedProblemDetails"
                }
              }
            }
          }
        }
      }
    },
    "/general/$metadata": {
      "get": {
        "tags": [
          "SecureMetadata"
        ],
        "summary": "Generates the general OData $metadata document.",
        "description": "- Required OAuth scope: None",
        "operationId": "GetGeneralMetadata",
        "responses": {
          "200": {
            "description": "General OData metadata document.",
            "content": {
              "application/xml": {
                "schema": {
                  "$ref": "#/components/schemas/GeneralMetadataResponse"
                }
              }
            }
          },
          "401": {
            "description": "Access token was invalid or expired.",
            "content": {
              "application/xml": {
                "schema": {
                  "$ref": "#/components/schemas/ExtendedProblemDetails"
                }
              },
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ExtendedProblemDetails"
                }
              }
            }
          },
          "404": {
            "description": "Operation unavailable.",
            "content": {
              "application/xml": {
                "schema": {
                  "$ref": "#/components/schemas/ExtendedProblemDetails"
                }
              },
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ExtendedProblemDetails"
                }
              }
            }
          },
          "429": {
            "description": "Rate limit was reached.",
            "content": {
              "application/xml": {
                "schema": {
                  "$ref": "#/components/schemas/ExtendedProblemDetails"
                }
              },
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ExtendedProblemDetails"
                }
              }
            }
          }
        }
      }
    },
    "/general": {
      "get": {
        "tags": [
          "SecureMetadata"
        ],
        "summary": "Generates the general OData service document.",
        "description": "- Required OAuth scope: None",
        "operationId": "GetGeneralODataServiceDocument",
        "responses": {
          "200": {
            "description": "General OData service document.",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ODataServiceDocumentElementCollectionResponse"
                }
              }
            }
          },
          "401": {
            "description": "Access token was invalid or expired.",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ExtendedProblemDetails"
                }
              }
            }
          },
          "404": {
            "description": "Operation unavailable.",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ExtendedProblemDetails"
                }
              }
            }
          },
          "429": {
            "description": "Rate limit was reached.",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ExtendedProblemDetails"
                }
              }
            }
          }
        }
      }
    },
    "/table/{tableName}": {
      "get": {
        "tags": [
          "Table"
        ],
        "summary": "Returns table rows for a specific table.",
        "description": "- Supported in $apply: aggregation (count, sum, average, min, max), groupby.\n- Supported OData function: toupper.\n- Supported $filter comparison operators: eq, ne, gt, ge, lt, le, in.\n- Supported OData logical operators: and, or, not.\n- Supported OData literal: null.\n- Number of rows in the response is returned in header X-APIServer-ResultCount.\n- Default page size is 1000.\n- Maximum page size is 1000.\n- Required OAuth scope: table.Read\n- More about <a href=\"https://docs.oasis-open.org/odata/odata/v4.01/odata-v4.01-part2-url-conventions.html#_Toc31360954\" target=\"_blank\">OData query options</a>\n- More about <a href=\"https://docs.oasis-open.org/odata/odata-data-aggregation-ext/v4.0/cs03/odata-data-aggregation-ext-v4.0-cs03.html#SystemQueryOptionapply\" target=\"_blank\">$apply</a>",
        "operationId": "GetTableRowListing",
        "parameters": [
          {
            "name": "tableName",
            "in": "path",
            "description": "Name of the table.",
            "required": true,
            "schema": {
              "type": "string"
            }
          },
          {
            "name": "Prefer",
            "in": "header",
            "description": "An optional OData header. Can be used to set the maximum page size using odata.maxpagesize.",
            "schema": {
              "type": "string"
            }
          },
          {
            "name": "$apply",
            "in": "query",
            "description": "Aggregation behavior is triggered using the query option $apply. It takes a sequence of set transformations, separated by forward slashes to express that they are consecutively applied, i.e., the result of each transformation is the input to the next transformation.",
            "schema": {
              "type": "string"
            }
          },
          {
            "name": "$filter",
            "in": "query",
            "description": "A function that must evaluate to true for a record to be returned.",
            "schema": {
              "type": "string"
            }
          },
          {
            "name": "$select",
            "in": "query",
            "description": "Limits the properties returned in the result.",
            "schema": {
              "type": "string"
            }
          },
          {
            "name": "$orderby",
            "in": "query",
            "description": "Specifies the order in which items are returned. The maximum number of expressions is 5.",
            "schema": {
              "type": "string"
            }
          },
          {
            "name": "$top",
            "in": "query",
            "description": "Limits the number of items returned from a collection.",
            "schema": {
              "type": "integer",
              "format": "int32"
            }
          },
          {
            "name": "$skip",
            "in": "query",
            "description": "Excludes the specified number of items of the queried collection from the result.",
            "schema": {
              "type": "integer",
              "format": "int32"
            }
          }
        ],
        "responses": {
          "200": {
            "description": "List/Query table content.",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/TableRowCollectionResponse"
                }
              }
            }
          },
          "400": {
            "description": "Invalid or bad request.",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ExtendedProblemDetails"
                }
              }
            }
          },
          "401": {
            "description": "Access token was invalid or expired.",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ExtendedProblemDetails"
                }
              }
            }
          },
          "403": {
            "description": "Access denied for the operation.",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ExtendedProblemDetails"
                }
              }
            }
          },
          "404": {
            "description": "Operation unavailable.",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ExtendedProblemDetails"
                }
              }
            }
          },
          "429": {
            "description": "Rate limit was reached.",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ExtendedProblemDetails"
                }
              }
            }
          }
        }
      },
      "post": {
        "tags": [
          "Table"
        ],
        "summary": "Adds a row to a table.",
        "description": "- Can specify _key in the body. If _key is not specified, it will be generated.\n- Required OAuth scope: table.Write",
        "operationId": "InsertTableRow",
        "parameters": [
          {
            "name": "tableName",
            "in": "path",
            "description": "Name of the table.",
            "required": true,
            "schema": {
              "type": "string"
            }
          }
        ],
        "requestBody": {
          "description": "Table row data.",
          "content": {
            "application/json": {
              "schema": {
                "type": "object",
                "additionalProperties": { }
              }
            }
          },
          "required": true
        },
        "responses": {
          "201": {
            "description": "Inserted a table row successfully.",
            "content": {
              "application/json": {
                "schema": {
                  "type": "object",
                  "additionalProperties": { }
                }
              }
            }
          },
          "400": {
            "description": "Invalid or bad request.",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ExtendedProblemDetails"
                }
              }
            }
          },
          "401": {
            "description": "Access token was invalid or expired.",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ExtendedProblemDetails"
                }
              }
            }
          },
          "403": {
            "description": "Access denied for the operation.",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ExtendedProblemDetails"
                }
              }
            }
          },
          "404": {
            "description": "Requested table ID not found, or operation unavailable.",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ExtendedProblemDetails"
                }
              }
            }
          },
          "429": {
            "description": "Rate limit was reached.",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ExtendedProblemDetails"
                }
              }
            }
          }
        }
      }
    },
    "/table/{tableName}('{key}')": {
      "get": {
        "tags": [
          "Table"
        ],
        "summary": "Retrieves a table row by key.",
        "description": "- Required OAuth scope: table.Read",
        "operationId": "GetTableRow",
        "parameters": [
          {
            "name": "tableName",
            "in": "path",
            "description": "Name of the table.",
            "required": true,
            "schema": {
              "type": "string"
            }
          },
          {
            "name": "key",
            "in": "path",
            "description": "The identifier of the table row.",
            "required": true,
            "schema": {
              "type": "string"
            }
          },
          {
            "name": "$select",
            "in": "query",
            "description": "Limits the properties returned in the result.",
            "schema": {
              "type": "string"
            }
          }
        ],
        "responses": {
          "200": {
            "description": "Retrieved a table row successfully.",
            "content": {
              "application/json": {
                "schema": {
                  "type": "object",
                  "additionalProperties": { }
                }
              }
            }
          },
          "400": {
            "description": "Invalid or bad request.",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ExtendedProblemDetails"
                }
              }
            }
          },
          "401": {
            "description": "Access token was invalid or expired.",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ExtendedProblemDetails"
                }
              }
            }
          },
          "403": {
            "description": "Access denied for the operation.",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ExtendedProblemDetails"
                }
              }
            }
          },
          "404": {
            "description": "Requested table ID or row key not found, or operation unavailable.",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ExtendedProblemDetails"
                }
              }
            }
          },
          "429": {
            "description": "Rate limit was reached.",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ExtendedProblemDetails"
                }
              }
            }
          }
        }
      },
      "delete": {
        "tags": [
          "Table"
        ],
        "summary": "Deletes a table row by key.",
        "description": "- Required OAuth scope: table.Write",
        "operationId": "DeleteSingleTableRow",
        "parameters": [
          {
            "name": "tableName",
            "in": "path",
            "description": "Name of the table.",
            "required": true,
            "schema": {
              "type": "string"
            }
          },
          {
            "name": "key",
            "in": "path",
            "description": "The identifier of the table row.",
            "required": true,
            "schema": {
              "type": "string"
            }
          }
        ],
        "responses": {
          "204": {
            "description": "Deleted a table row successfully."
          },
          "400": {
            "description": "Invalid or bad request.",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ExtendedProblemDetails"
                }
              }
            }
          },
          "401": {
            "description": "Access token was invalid or expired.",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ExtendedProblemDetails"
                }
              }
            }
          },
          "403": {
            "description": "Access denied for the operation.",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ExtendedProblemDetails"
                }
              }
            }
          },
          "404": {
            "description": "Requested table ID or row key not found, or operation unavailable.",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ExtendedProblemDetails"
                }
              }
            }
          },
          "429": {
            "description": "Rate limit was reached.",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ExtendedProblemDetails"
                }
              }
            }
          }
        }
      },
      "patch": {
        "tags": [
          "Table"
        ],
        "summary": "Upserts or updates a table row by key.",
        "description": "- If If-Match: * is included, the request is treated as an update. Otherwise, the request is treated as an upsert.\n- \\* is the only accepted value for If-Match.\n- Etag other than If-Match will be ignored.\n- Required OAuth scope: table.Write",
        "operationId": "UpsertTableRow",
        "parameters": [
          {
            "name": "tableName",
            "in": "path",
            "description": "Name of the table.",
            "required": true,
            "schema": {
              "type": "string"
            }
          },
          {
            "name": "key",
            "in": "path",
            "description": "The identifier of the table row.",
            "required": true,
            "schema": {
              "type": "string"
            }
          },
          {
            "name": "If-Match",
            "in": "header",
            "description": "If value is *, request is treated as an update. If empty, request is treated as an upsert.",
            "schema": {
              "type": "string"
            }
          }
        ],
        "requestBody": {
          "description": "Table row data.",
          "content": {
            "application/json": {
              "schema": {
                "type": "object",
                "additionalProperties": { }
              }
            }
          },
          "required": true
        },
        "responses": {
          "201": {
            "description": "Inserted a table row successfully.",
            "content": {
              "application/json": {
                "schema": {
                  "type": "object",
                  "additionalProperties": { }
                }
              }
            }
          },
          "204": {
            "description": "Updated a table row successfully."
          },
          "400": {
            "description": "Invalid or bad request. If row key is not found, error \"No row was updated.\" is returned.",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ExtendedProblemDetails"
                }
              }
            }
          },
          "401": {
            "description": "Access token was invalid or expired.",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ExtendedProblemDetails"
                }
              }
            }
          },
          "403": {
            "description": "Access denied for the operation.",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ExtendedProblemDetails"
                }
              }
            }
          },
          "404": {
            "description": "Requested table ID not found, or operation unavailable.",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ExtendedProblemDetails"
                }
              }
            }
          },
          "429": {
            "description": "Rate limit was reached.",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ExtendedProblemDetails"
                }
              }
            }
          }
        }
      }
    },
    "/table/{tableName}/ReplaceAllRowsAsync": {
      "post": {
        "tags": [
          "Table"
        ],
        "summary": "Replaces an existing table with data from a file with supported format.",
        "description": "- Supported file formats can be found <a href=\"https://doc.laserfiche.com/laserfiche.documentation/en-us/Default.htm#../Subsystems/ProcessAutomation/Content/Resources/Entities/lookup-tables.htm\" target=\"_blank\">here</a>.\n- Primary key column \"_key\" cannot be included in the file data.\n- If the operation failed for any reason, e.g., type change in column, the table data will remain unaffected.\n- Required OAuth scope: table.Write",
        "operationId": "ReplaceTable",
        "parameters": [
          {
            "name": "tableName",
            "in": "path",
            "description": "Name of the table.",
            "required": true,
            "schema": {
              "type": "string"
            }
          }
        ],
        "requestBody": {
          "content": {
            "multipart/form-data": {
              "schema": {
                "required": [
                  "file"
                ],
                "type": "object",
                "properties": {
                  "file": {
                    "type": "string",
                    "description": "The file containing the new data for the table.",
                    "format": "binary"
                  }
                }
              },
              "encoding": {
                "file": {
                  "style": "form"
                }
              }
            }
          }
        },
        "responses": {
          "202": {
            "description": "A long operation task ID.",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/StartTaskResponse"
                }
              }
            }
          },
          "400": {
            "description": "Invalid or bad request.",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ExtendedProblemDetails"
                }
              }
            }
          },
          "401": {
            "description": "Access token was invalid or expired.",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ExtendedProblemDetails"
                }
              }
            }
          },
          "403": {
            "description": "Access denied for the operation.",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ExtendedProblemDetails"
                }
              }
            }
          },
          "404": {
            "description": "Requested table not found, or operation unavailable.",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ExtendedProblemDetails"
                }
              }
            }
          },
          "413": {
            "description": "Request was too large.",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ExtendedProblemDetails"
                }
              }
            }
          },
          "429": {
            "description": "Rate limit was reached.",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ExtendedProblemDetails"
                }
              }
            }
          }
        }
      }
    },
    "/general/Tasks({id})": {
      "get": {
        "tags": [
          "Task"
        ],
        "summary": "Returns the status of a single task.",
        "description": "- Required OAuth scope: None",
        "operationId": "GetTask",
        "parameters": [
          {
            "name": "id",
            "in": "path",
            "description": "The identifier of the task.",
            "required": true,
            "schema": {
              "type": "string",
              "format": "uuid"
            }
          }
        ],
        "responses": {
          "200": {
            "description": "The status of the task.",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/TaskProgress"
                }
              }
            }
          },
          "400": {
            "description": "Invalid or bad request.",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ExtendedProblemDetails"
                }
              }
            }
          },
          "401": {
            "description": "Access token was invalid or expired.",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ExtendedProblemDetails"
                }
              }
            }
          },
          "403": {
            "description": "Access denied for the operation.",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ExtendedProblemDetails"
                }
              }
            }
          },
          "404": {
            "description": "Requested task ID not found, or operation unavailable.",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ExtendedProblemDetails"
                }
              }
            }
          },
          "429": {
            "description": "Rate limit was reached.",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ExtendedProblemDetails"
                }
              }
            }
          }
        }
      },
      "delete": {
        "tags": [
          "Task"
        ],
        "summary": "Starts the cancellation of a task.",
        "description": "- Required OAuth scope: None",
        "operationId": "CancelTask",
        "parameters": [
          {
            "name": "id",
            "in": "path",
            "description": "The identifier of the task.",
            "required": true,
            "schema": {
              "type": "string",
              "format": "uuid"
            }
          }
        ],
        "responses": {
          "204": {
            "description": "Task cancelled successfully."
          },
          "400": {
            "description": "Invalid or bad request.",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ExtendedProblemDetails"
                }
              }
            }
          },
          "401": {
            "description": "Access token was invalid or expired.",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ExtendedProblemDetails"
                }
              }
            }
          },
          "403": {
            "description": "Access denied for the operation.",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ExtendedProblemDetails"
                }
              }
            }
          },
          "404": {
            "description": "Requested task ID not found, or operation unavailable.",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ExtendedProblemDetails"
                }
              }
            }
          },
          "429": {
            "description": "Rate limit was reached.",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ExtendedProblemDetails"
                }
              }
            }
          }
        }
      }
    }
  },
  "components": {
    "schemas": {
      "ExtendedProblemDetails": {
        "type": "object",
        "properties": {
          "operationId": {
            "type": "string",
            "nullable": true
          },
          "errorSource": {
            "type": "string",
            "nullable": true
          },
          "errorCode": {
            "type": "integer",
            "format": "int32",
            "nullable": true
          },
          "traceId": {
            "type": "string",
            "nullable": true
          },
          "type": {
            "type": "string",
            "nullable": true
          },
          "title": {
            "type": "string",
            "nullable": true
          },
          "status": {
            "type": "integer",
            "format": "int32",
            "nullable": true
          },
          "detail": {
            "type": "string",
            "nullable": true
          },
          "instance": {
            "type": "string",
            "nullable": true
          }
        },
        "additionalProperties": { }
      },
      "GeneralMetadataResponse": {
        "type": "object",
        "additionalProperties": false,
        "description": "A placeholder class for General OData EDM metadata.",
        "example": "<?xml version=\"1.0\" encoding=\"utf-8\"?>\r\n  <edmx:Edmx Version=\"4.0\" xmlns:edmx=\"http://docs.oasis-open.org/odata/ns/edmx\">\r\n    <edmx:DataServices>\r\n      <Schema Namespace=\"string\" xmlns=\"http://docs.oasis-open.org/odata/ns/edm\">\r\n        <EntityType Name=\"string\">\r\n          <Key>\r\n            <PropertyRef Name=\"string\" />\r\n          </Key>\r\n          <Property Name=\"string\" Type=\"string\" Nullable=\"false\" />\r\n        </EntityType>\r\n      </Schema>\r\n      <Schema Namespace=\"string\" xmlns=\"http://docs.oasis-open.org/odata/ns/edm\">\r\n        <EntityContainer Name=\"string\">\r\n          <EntitySet Name=\"string\" EntityType=\"string\" />\r\n        </EntityContainer>\r\n      </Schema>\r\n    </edmx:DataServices>\r\n  </edmx:Edmx>"
      },
      "ODataServiceDocumentElement": {
        "type": "object",
        "properties": {
          "name": {
            "type": "string",
            "description": "The name of the element.",
            "nullable": true
          },
          "kind": {
            "type": "string",
            "description": "The kind of navigation source.",
            "nullable": true
          },
          "url": {
            "type": "string",
            "description": "The URI representing the Unified Resource Locator (URL) to the element.",
            "nullable": true
          }
        },
        "additionalProperties": false,
        "description": "Class representing an element in a service document."
      },
      "ODataServiceDocumentElementCollectionResponse": {
        "required": [
          "value"
        ],
        "type": "object",
        "properties": {
          "@odata.context": {
            "type": "string",
            "description": "It contains OData context.",
            "nullable": true
          },
          "value": {
            "type": "array",
            "items": {
              "$ref": "#/components/schemas/ODataServiceDocumentElement"
            },
            "nullable": true
          }
        },
        "additionalProperties": false,
        "description": "Response when getting a list of OData service document elements."
      },
      "OperationResult": {
        "type": "object",
        "additionalProperties": false
      },
      "OperationStatus": {
        "enum": [
          "NotStarted",
          "InProgress",
          "Completed",
          "Failed",
          "Cancelled",
          "Unknown"
        ],
        "type": "string"
      },
      "OperationType": {
        "enum": [
          "ReplaceTable"
        ],
        "type": "string"
      },
      "StartTaskResponse": {
        "type": "object",
        "properties": {
          "taskId": {
            "type": "string",
            "description": "Task identifier that can be used to check on the status of the operation.",
            "format": "uuid"
          }
        },
        "additionalProperties": false,
        "description": "Success response when a task is started."
      },
      "TableMetadataResponse": {
        "type": "object",
        "additionalProperties": false,
        "description": "A placeholder class for Table OData EDM metadata.",
        "example": "<?xml version=\"1.0\" encoding=\"utf-8\"?>\r\n  <edmx:Edmx Version=\"4.0\" xmlns:edmx=\"http://docs.oasis-open.org/odata/ns/edmx\">\r\n    <edmx:DataServices>\r\n      <Schema Namespace=\"string\" xmlns=\"http://docs.oasis-open.org/odata/ns/edm\">\r\n        <EntityType Name=\"string\">\r\n          <Key>\r\n            <PropertyRef Name=\"string\" />\r\n          </Key>\r\n          <Property Name=\"string\" Type=\"string\" />\r\n        </EntityType>\r\n        <Action Name=\"string\" IsBound=\"true\" EntitySetPath=\"string\">\r\n          <Parameter Name=\"string\" Type=\"string\" Nullable=\"false\" />\r\n          <ReturnType Type=\"string\" Nullable=\"false\" />\r\n        </Action>\r\n        <EntityContainer Name=\"string\">\r\n          <EntitySet Name=\"string\" EntityType=\"string\" />\r\n        </EntityContainer>\r\n      </Schema>\r\n    </edmx:DataServices>\r\n  </edmx:Edmx>"
      },
      "TableRowCollectionResponse": {
        "required": [
          "value"
        ],
        "type": "object",
        "properties": {
          "@odata.nextLink": {
            "type": "string",
            "description": "It contains a URL that allows retrieving the next subset of the requested collection.",
            "nullable": true
          },
          "@odata.context": {
            "type": "string",
            "description": "It contains OData context.",
            "nullable": true
          },
          "value": {
            "type": "array",
            "items": {
              "type": "object",
              "additionalProperties": { }
            },
            "nullable": true
          }
        },
        "additionalProperties": false,
        "description": "Response when getting a list of table rows."
      },
      "TaskProgress": {
        "type": "object",
        "properties": {
          "id": {
            "type": "string",
            "description": "Identifier of the associated task.",
            "format": "uuid"
          },
          "type": {
            "$ref": "#/components/schemas/OperationType"
          },
          "status": {
            "$ref": "#/components/schemas/OperationStatus"
          },
          "errors": {
            "type": "array",
            "items": {
              "$ref": "#/components/schemas/ExtendedProblemDetails"
            },
            "description": "A list of errors occurred during the execution of the associated task.",
            "nullable": true
          },
          "result": {
            "$ref": "#/components/schemas/OperationResult"
          },
          "startTime": {
            "type": "string",
            "description": "The timestamp representing when the associated task is started.",
            "format": "date-time"
          },
          "lastUpdateTime": {
            "type": "string",
            "description": "The timestamp representing the last time when the associated task's status has changed.",
            "format": "date-time"
          }
        },
        "additionalProperties": false,
        "description": "Task progress."
      }
    },
    "securitySchemes": {
      "Basic": {
        "type": "http",
        "description": "<p>Enter the Service App Basic Authentication credentials.</p>",
        "scheme": "basic"
      },
      "OAuth AccessToken": {
        "type": "http",
        "description": "Enter <strong>Access Token</strong> into the textbox.",
        "scheme": "bearer"
      },
      "OAuth2 Authorization Code Flow": {
        "type": "oauth2",
        "description": "<p>Note: Please type the client_id/client_secret of a registered web application, or the client_id of an SPA. For an SPA, the client_secret field must be left empty. The app, either a web application or SPA, must have the following URI defined as its redirect URI.</p><p>https://api.laserfiche.com/odata4/swagger/oauth2-redirect.html</p><p>For more information, including how to configure project scopes see <a href=\"https://developer.laserfiche.com/guides/guide_authenticating-to-the-swagger-playground.html\" target=\"_blank\">this page</a></p>",
        "flows": {
          "authorizationCode": {
            "authorizationUrl": "https://signin.laserfiche.com/oauth/Authorize",
            "tokenUrl": "https://signin.laserfiche.com/oauth/Token",
            "scopes": {
              "table.Read": "Allows the app to read the content of lookup tables on behalf of the signed-in user.",
              "table.Write": "Allows the app to modify the content of lookup tables on behalf of the signed-in user.",
              "project/Global": "Allows the app to modify the content of global lookup tables on behalf of the signed-in user. User must also have access to global resources in order for the application to access these tables.",
              "project/Swagger+Test+Project": "Allows the app to modify the content of lookup tables in a test project named 'Swagger Test Project'. If this project doesn't exist, you can create it for testing purposes."
            }
          }
        }
      }
    }
  },
  "security": [
    {
      "Basic": [ ],
      "OAuth AccessToken": [
        "DemoSwaggerDifferentAuthScheme"
      ],
      "OAuth2 Authorization Code Flow": [
        "DemoSwaggerDifferentAuthScheme"
      ]
    }
  ]
}