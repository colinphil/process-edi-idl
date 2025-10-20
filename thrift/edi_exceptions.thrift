/**
 * EDI Service Exceptions
 * 
 * This file contains all the exception definitions for the EDI service,
 * mapping to the error types defined in the Smithy service.
 */

namespace java com.colinleephillips.process.edi.thrift
namespace py com.colinleephillips.process.edi.thrift
namespace go com.colinleephillips.process.edi.thrift

// ============================================================================
// Exception Definitions
// ============================================================================

/**
 * Validation error - client error (400)
 */
exception ValidationError {
    1: required string message,
    2: optional string code,
    3: optional string field,
    4: optional i32 lineNumber
}

/**
 * Parsing error - client error (400)
 */
exception ParsingError {
    1: required string message,
    2: optional string code,
    3: optional string field,
    4: optional i32 lineNumber
}

/**
 * Business rule error - client error (422)
 */
exception BusinessRuleError {
    1: required string message,
    2: optional string code,
    3: optional string field,
    4: optional i32 lineNumber
}

/**
 * Unsupported message type error - client error (415)
 */
exception UnsupportedMessageTypeError {
    1: required string message,
    2: optional string code,
    3: optional string messageType
}

/**
 * Internal error - server error (500)
 */
exception InternalError {
    1: required string message,
    2: optional string code
}
