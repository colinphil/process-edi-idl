# Thrift EDI Service Usage Examples

This document provides examples of how to use the Thrift EDI service for processing different types of EDI messages.

## Overview

The Thrift EDI service provides a unified API for processing multiple EDI message types including:
- EDI 850 (Purchase Order)
- EDI 810 (Invoice)
- EDI 856 (Advance Ship Notice)
- EDI 997 (Functional Acknowledgment)

## Service Operations

### 1. Process EDI Message

The main operation for processing EDI messages of any supported type.

#### Example: Processing an EDI 850 Purchase Order

```python
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from edi_service import EdiService
from edi_types import *

# Create transport and protocol
transport = TSocket.TSocket('localhost', 9090)
transport = TTransport.TBufferedTransport(transport)
protocol = TBinaryProtocol.TBinaryProtocol(transport)

# Create client
client = EdiService.Client(protocol)

# Open connection
transport.open()

# Prepare EDI 850 message
edi_message = """ISA*00*          *00*          *ZZ*SENDER         *ZZ*RECEIVER       *210101*1200*^*00501*000000001*0*P*>~
GS*PO*SENDER*RECEIVER*20210101*1200*1*X*005010~
ST*850*0001~
BEG*00*SA*PO123456**20210101~
REF*DP*DEPARTMENT123~
N1*BY*ACME CORP*92*12345~
N3*123 MAIN ST~
N4*NEW YORK*NY*10001~
N1*ST*ACME CORP*92*12345~
N3*123 MAIN ST~
N4*NEW YORK*NY*10001~
PO1*1*10*EA*25.50**VP*SKU123*PD*WIDGET~
PO1*2*5*EA*15.75**VP*SKU456*PD*GADGET~
CTT*2~
SE*15*0001~
GE*1*1~
IEA*1*000000001~"""

# Create request
request = ProcessEdiMessageRequest(
    ediMessage=edi_message,
    messageType="850",
    customerId="CUSTOMER123",
    options=ProcessingOptions(
        validateFormat=True,
        validateBusinessRules=True,
        includeParsingDetails=True,
        includeRawSegments=True
    )
)

try:
    # Process the EDI message
    response = client.processEdiMessage(request)
    
    print(f"Processing Status: {response.status}")
    print(f"Message Type: {response.messageType}")
    print(f"Processed At: {response.processedAt}")
    
    if response.purchaseOrder:
        po = response.purchaseOrder
        print(f"PO Number: {po.poNumber}")
        print(f"PO Date: {po.poDate}")
        print(f"Number of Line Items: {len(po.lineItems)}")
        
        for item in po.lineItems:
            print(f"  Line {item.lineNumber}: {item.product.description} - Qty: {item.quantityOrdered.value}")
    
    if response.messages:
        print("Processing Messages:")
        for msg in response.messages:
            print(f"  {msg.level}: {msg.message}")
            
except ValidationError as e:
    print(f"Validation Error: {e.message}")
except ParsingError as e:
    print(f"Parsing Error: {e.message}")
except BusinessRuleError as e:
    print(f"Business Rule Error: {e.message}")
except UnsupportedMessageTypeError as e:
    print(f"Unsupported Message Type: {e.messageType}")
except InternalError as e:
    print(f"Internal Error: {e.message}")

finally:
    transport.close()
```

#### Example: Processing an EDI 810 Invoice

```python
# EDI 810 Invoice message
edi_invoice = """ISA*00*          *00*          *ZZ*SENDER         *ZZ*RECEIVER       *210101*1200*^*00501*000000002*0*P*>~
GS*IN*SENDER*RECEIVER*20210101*1200*2*X*005010~
ST*810*0001~
BIG*20210101*INV123456**20210201~
REF*PO*PO123456~
N1*BT*ACME CORP*92*12345~
N3*123 MAIN ST~
N4*NEW YORK*NY*10001~
N1*ST*ACME CORP*92*12345~
N3*123 MAIN ST~
N4*NEW YORK*NY*10001~
IT1*1*10*EA*25.50**VP*SKU123*PD*WIDGET~
IT1*2*5*EA*15.75**VP*SKU456*PD*GADGET~
TDS*255~
CTT*2~
SE*15*0001~
GE*1*2~
IEA*1*000000002~"""

request = ProcessEdiMessageRequest(
    ediMessage=edi_invoice,
    messageType="810",
    customerId="CUSTOMER123"
)

try:
    response = client.processEdiMessage(request)
    
    if response.invoice:
        invoice = response.invoice
        print(f"Invoice Number: {invoice.invoiceNumber}")
        print(f"Invoice Date: {invoice.invoiceDate}")
        print(f"Due Date: {invoice.dueDate}")
        
        if invoice.monetaryAmounts and invoice.monetaryAmounts.totalAmount:
            print(f"Total Amount: {invoice.monetaryAmounts.totalAmount.value} {invoice.monetaryAmounts.totalAmount.currencyCode}")
            
except Exception as e:
    print(f"Error processing invoice: {e}")
```

### 2. Get Supported Message Types

Retrieve a list of all supported EDI message types.

```python
# Create request
request = GetSupportedMessageTypesRequest(customerId="CUSTOMER123")

try:
    response = client.getSupportedMessageTypes(request)
    
    print("Supported EDI Message Types:")
    for msg_type in response.supportedTypes:
        print(f"  {msg_type.code}: {msg_type.name}")
        print(f"    Description: {msg_type.description}")
        print(f"    Supported: {msg_type.supported}")
        if msg_type.requiredSegments:
            print(f"    Required Segments: {', '.join(msg_type.requiredSegments)}")
        print()
        
except Exception as e:
    print(f"Error getting supported types: {e}")
```

### 3. Validate EDI Message

Validate EDI message format without full processing.

```python
# Create validation request
request = ValidateEdiMessageRequest(
    ediMessage=edi_message,
    messageType="850",
    customerId="CUSTOMER123"
)

try:
    response = client.validateEdiMessage(request)
    
    print(f"Validation Status: {response.status}")
    print(f"Detected Message Type: {response.detectedMessageType}")
    print(f"EDI Version: {response.ediVersion}")
    
    if response.messages:
        print("Validation Messages:")
        for msg in response.messages:
            print(f"  {msg.level}: {msg.message}")
            if msg.field:
                print(f"    Field: {msg.field}")
            if msg.lineNumber:
                print(f"    Line: {msg.lineNumber}")
                
except ValidationError as e:
    print(f"Validation Error: {e.message}")
except ParsingError as e:
    print(f"Parsing Error: {e.message}")
```

## Java Example

```java
import org.apache.thrift.transport.TSocket;
import org.apache.thrift.transport.TTransport;
import org.apache.thrift.protocol.TBinaryProtocol;
import com.colinleephillips.process.edi.thrift.*;

public class EdiServiceClient {
    public static void main(String[] args) {
        try {
            // Create transport and protocol
            TTransport transport = new TSocket("localhost", 9090);
            transport.open();
            TBinaryProtocol protocol = new TBinaryProtocol(transport);
            
            // Create client
            EdiService.Client client = new EdiService.Client(protocol);
            
            // Prepare request
            ProcessEdiMessageRequest request = new ProcessEdiMessageRequest();
            request.setEdiMessage(ediMessage);
            request.setMessageType("850");
            request.setCustomerId("CUSTOMER123");
            
            ProcessingOptions options = new ProcessingOptions();
            options.setValidateFormat(true);
            options.setValidateBusinessRules(true);
            options.setIncludeParsingDetails(true);
            request.setOptions(options);
            
            // Process EDI message
            ProcessEdiMessageResponse response = client.processEdiMessage(request);
            
            System.out.println("Processing Status: " + response.getStatus());
            System.out.println("Message Type: " + response.getMessageType());
            
            if (response.getPurchaseOrder() != null) {
                PurchaseOrderData po = response.getPurchaseOrder();
                System.out.println("PO Number: " + po.getPoNumber());
                System.out.println("PO Date: " + po.getPoDate());
                
                if (po.getLineItems() != null) {
                    for (PurchaseOrderLineItem item : po.getLineItems()) {
                        System.out.println("Line " + item.getLineNumber() + 
                                         ": " + item.getProduct().getDescription());
                    }
                }
            }
            
            transport.close();
            
        } catch (ValidationError e) {
            System.err.println("Validation Error: " + e.getMessage());
        } catch (ParsingError e) {
            System.err.println("Parsing Error: " + e.getMessage());
        } catch (Exception e) {
            System.err.println("Error: " + e.getMessage());
        }
    }
}
```

## Go Example

```go
package main

import (
    "fmt"
    "git.apache.org/thrift/lib/go/thrift"
    "com.colinleephillips/process/edi/thrift"
)

func main() {
    // Create transport
    transport, err := thrift.NewTSocket("localhost:9090")
    if err != nil {
        fmt.Printf("Error creating transport: %v\n", err)
        return
    }
    
    // Open transport
    if err := transport.Open(); err != nil {
        fmt.Printf("Error opening transport: %v\n", err)
        return
    }
    defer transport.Close()
    
    // Create protocol and client
    protocol := thrift.NewTBinaryProtocolTransport(transport)
    client := edi_service.NewEdiServiceClientProtocol(transport, protocol, protocol)
    
    // Prepare request
    request := &edi_types.ProcessEdiMessageRequest{
        EdiMessage:  ediMessage,
        MessageType: "850",
        CustomerId:  stringPtr("CUSTOMER123"),
        Options: &edi_types.ProcessingOptions{
            ValidateFormat:         boolPtr(true),
            ValidateBusinessRules:  boolPtr(true),
            IncludeParsingDetails: boolPtr(true),
        },
    }
    
    // Process EDI message
    response, err := client.ProcessEdiMessage(request)
    if err != nil {
        fmt.Printf("Error processing EDI message: %v\n", err)
        return
    }
    
    fmt.Printf("Processing Status: %v\n", response.Status)
    fmt.Printf("Message Type: %s\n", response.MessageType)
    
    if response.PurchaseOrder != nil {
        po := response.PurchaseOrder
        fmt.Printf("PO Number: %s\n", po.PoNumber)
        if po.PoDate != nil {
            fmt.Printf("PO Date: %s\n", *po.PoDate)
        }
        
        if po.LineItems != nil {
            for _, item := range po.LineItems {
                fmt.Printf("Line %s: %s\n", item.LineNumber, 
                          item.Product.Description)
            }
        }
    }
}

func stringPtr(s string) *string {
    return &s
}

func boolPtr(b bool) *bool {
    return &b
}
```

## Error Handling

The service defines several specific exceptions for different error conditions:

- **ValidationError**: EDI message format is invalid (HTTP 400)
- **ParsingError**: EDI message cannot be parsed (HTTP 400)
- **BusinessRuleError**: Business rules are violated (HTTP 422)
- **UnsupportedMessageTypeError**: Message type is not supported (HTTP 415)
- **InternalError**: Internal server error (HTTP 500)

Always handle these exceptions appropriately in your client code to provide meaningful error messages to users.

## Configuration

The service supports various processing options:

- `validateFormat`: Validate EDI format structure
- `validateBusinessRules`: Perform business rule validation
- `includeParsingDetails`: Include detailed parsing information
- `includeRawSegments`: Include raw parsed segments
- `environment`: Target processing environment
- `validationRules`: Custom validation rules

These options can be set in the `ProcessingOptions` structure when making requests.
