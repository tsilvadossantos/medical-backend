#!/bin/bash

# Medical Backend API - Client Test Script
# Tests all features of the API

# Don't exit on error - we want to continue testing and report failures
# set -e

BASE_URL="${BASE_URL:-http://localhost:8000}"
# Note: API endpoints are at root level, not /api/v1
API_URL="$BASE_URL"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
PASSED=0
FAILED=0

# Helper functions
print_header() {
    echo ""
    echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
}

print_test() {
    echo -e "\n${YELLOW}▶ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
    ((PASSED++))
}

print_failure() {
    echo -e "${RED}✗ $1${NC}"
    ((FAILED++))
}

print_info() {
    echo -e "  ${NC}$1${NC}"
}

# Check if jq is installed
if ! command -v jq &> /dev/null; then
    echo -e "${RED}Error: jq is required but not installed.${NC}"
    echo "Install with: brew install jq (Mac) or apt-get install jq (Linux)"
    exit 1
fi

# Check if API is running
print_header "Checking API Health"
if curl -s "$BASE_URL/health" | jq -e '.status == "ok"' > /dev/null 2>&1; then
    print_success "API is healthy"
else
    print_failure "API is not responding at $BASE_URL"
    echo "Make sure the containers are running: ./scripts/start.sh"
    exit 1
fi

# ============================================================================
# HEALTH & METRICS
# ============================================================================
print_header "Testing Health & Metrics Endpoints"

print_test "GET /health"
RESPONSE=$(curl -s "$BASE_URL/health")
if echo "$RESPONSE" | jq -e '.status == "ok"' > /dev/null; then
    print_success "Health check passed"
else
    print_failure "Health check failed"
fi

print_test "GET /metrics"
RESPONSE=$(curl -s "$BASE_URL/metrics")
if echo "$RESPONSE" | grep -q "http_requests_total"; then
    print_success "Metrics endpoint returns Prometheus metrics"
    print_info "Sample metrics available: http_requests_total, patients_created_total, etc."
else
    print_failure "Metrics endpoint not working"
fi

# ============================================================================
# PATIENT CRUD OPERATIONS
# ============================================================================
print_header "Testing Patient CRUD Operations"

# Create Patient 1
print_test "POST /patients - Create first patient"
PATIENT1=$(curl -s -X POST "$API_URL/patients" \
    -H "Content-Type: application/json" \
    -d '{
        "name": "John Smith",
        "date_of_birth": "1979-03-15"
    }')
PATIENT1_ID=$(echo "$PATIENT1" | jq -r '.id')
if [ "$PATIENT1_ID" != "null" ] && [ -n "$PATIENT1_ID" ]; then
    print_success "Created patient: ID=$PATIENT1_ID, Name=$(echo "$PATIENT1" | jq -r '.name')"
else
    print_failure "Failed to create patient"
    echo "$PATIENT1"
fi

# Create Patient 2
print_test "POST /patients - Create second patient"
PATIENT2=$(curl -s -X POST "$API_URL/patients" \
    -H "Content-Type: application/json" \
    -d '{
        "name": "Jane Doe",
        "date_of_birth": "1985-07-22"
    }')
PATIENT2_ID=$(echo "$PATIENT2" | jq -r '.id')
if [ "$PATIENT2_ID" != "null" ] && [ -n "$PATIENT2_ID" ]; then
    print_success "Created patient: ID=$PATIENT2_ID, Name=$(echo "$PATIENT2" | jq -r '.name')"
else
    print_failure "Failed to create patient"
fi

# Create Patient 3
print_test "POST /patients - Create third patient"
PATIENT3=$(curl -s -X POST "$API_URL/patients" \
    -H "Content-Type: application/json" \
    -d '{
        "name": "Robert Johnson",
        "date_of_birth": "1992-11-08"
    }')
PATIENT3_ID=$(echo "$PATIENT3" | jq -r '.id')
if [ "$PATIENT3_ID" != "null" ] && [ -n "$PATIENT3_ID" ]; then
    print_success "Created patient: ID=$PATIENT3_ID"
else
    print_failure "Failed to create patient"
fi

# Get single patient
print_test "GET /patients/{id} - Get patient by ID"
RESPONSE=$(curl -s "$API_URL/patients/$PATIENT1_ID")
if echo "$RESPONSE" | jq -e ".id == $PATIENT1_ID" > /dev/null; then
    print_success "Retrieved patient $PATIENT1_ID successfully"
else
    print_failure "Failed to get patient"
fi

# List all patients
print_test "GET /patients - List all patients"
RESPONSE=$(curl -s "$API_URL/patients")
TOTAL=$(echo "$RESPONSE" | jq -r '.total')
if [ "$TOTAL" -ge 3 ]; then
    print_success "Listed patients: total=$TOTAL"
else
    print_failure "Failed to list patients"
fi

# Test pagination
print_test "GET /patients?page=1&size=2 - Test pagination"
RESPONSE=$(curl -s "$API_URL/patients?page=1&size=2")
ITEMS=$(echo "$RESPONSE" | jq '.items | length')
PAGES=$(echo "$RESPONSE" | jq '.pages')
if [ "$ITEMS" -eq 2 ]; then
    print_success "Pagination works: got $ITEMS items, total pages=$PAGES"
else
    print_failure "Pagination failed"
fi

# Test sorting
print_test "GET /patients?sort_by=name&sort_order=asc - Test sorting"
RESPONSE=$(curl -s "$API_URL/patients?sort_by=name&sort_order=asc")
FIRST_NAME=$(echo "$RESPONSE" | jq -r '.items[0].name')
if [ -n "$FIRST_NAME" ]; then
    print_success "Sorting works: first patient by name = $FIRST_NAME"
else
    print_failure "Sorting failed"
fi

# Test search
print_test "GET /patients?search=John - Test search"
RESPONSE=$(curl -s "$API_URL/patients?search=John")
TOTAL=$(echo "$RESPONSE" | jq -r '.total')
if [ "$TOTAL" -ge 1 ]; then
    print_success "Search works: found $TOTAL patient(s) matching 'John'"
else
    print_failure "Search failed"
fi

# Test invalid sort_by (should return 400)
print_test "GET /patients?sort_by=invalid - Test validation"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL/patients?sort_by=invalid")
if [ "$HTTP_CODE" -eq 400 ]; then
    print_success "Validation works: invalid sort_by returns 400"
else
    print_failure "Validation failed: expected 400, got $HTTP_CODE"
fi

# Update patient
print_test "PUT /patients/{id} - Update patient"
RESPONSE=$(curl -s -X PUT "$API_URL/patients/$PATIENT1_ID" \
    -H "Content-Type: application/json" \
    -d '{
        "name": "John A. Smith"
    }')
NEW_NAME=$(echo "$RESPONSE" | jq -r '.name')
if [ "$NEW_NAME" = "John A. Smith" ]; then
    print_success "Updated patient name to: $NEW_NAME"
else
    print_failure "Failed to update patient"
fi

# ============================================================================
# NOTE OPERATIONS
# ============================================================================
print_header "Testing Note Operations"

# Create SOAP note 1
print_test "POST /patients/{id}/notes - Create SOAP note"
NOTE1=$(curl -s -X POST "$API_URL/patients/$PATIENT1_ID/notes" \
    -H "Content-Type: application/json" \
    -d '{
        "content": "SOAP Note - Encounter Date: 2024-01-15\nPatient: patient--001\n\nS: 45 y/o male presenting with chest pain x 2 hours. Sharp, substernal, radiates to left arm.\n\nO:\nVitals:\nBP: 145/92 mmHg\nHR: 102 bpm\nECG: ST elevation V1-V4\n\nA:\nAcute STEMI - anterior wall\n\nP:\nActivate cath lab\nAspirin 325mg\nHeparin drip\n\nSigned:\nDr. Sarah Chen, MD",
        "note_timestamp": "2024-01-15T09:00:00Z"
    }')
NOTE1_ID=$(echo "$NOTE1" | jq -r '.id')
if [ "$NOTE1_ID" != "null" ] && [ -n "$NOTE1_ID" ]; then
    print_success "Created note: ID=$NOTE1_ID"
else
    print_failure "Failed to create note"
fi

# Create SOAP note 2
print_test "POST /patients/{id}/notes - Create follow-up note"
NOTE2=$(curl -s -X POST "$API_URL/patients/$PATIENT1_ID/notes" \
    -H "Content-Type: application/json" \
    -d '{
        "content": "SOAP Note - Encounter Date: 2024-01-16\nPatient: patient--001\n\nS: Post-cath day 1. Significant improvement in chest pain.\n\nO:\nVitals stable\nBP: 128/78\nAccess site: no hematoma\n\nA:\nSTEMI s/p successful PCI to LAD\n\nP:\nContinue dual antiplatelet\nCardiac rehab referral\nDischarge tomorrow\n\nSigned:\nDr. Michael Torres, MD",
        "note_timestamp": "2024-01-16T08:00:00Z"
    }')
NOTE2_ID=$(echo "$NOTE2" | jq -r '.id')
if [ "$NOTE2_ID" != "null" ] && [ -n "$NOTE2_ID" ]; then
    print_success "Created follow-up note: ID=$NOTE2_ID"
else
    print_failure "Failed to create note"
fi

# List patient notes
print_test "GET /patients/{id}/notes - List patient notes"
RESPONSE=$(curl -s "$API_URL/patients/$PATIENT1_ID/notes")
NOTE_COUNT=$(echo "$RESPONSE" | jq -r '.total')
if [ "$NOTE_COUNT" -ge 2 ]; then
    print_success "Listed notes: total=$NOTE_COUNT"
else
    print_failure "Failed to list notes"
fi

# ============================================================================
# SUMMARY GENERATION
# ============================================================================
print_header "Testing Summary Generation"

# Synchronous summary - clinician audience
print_test "GET /patients/{id}/summary?audience=clinician - Sync summary (clinician)"
RESPONSE=$(curl -s "$API_URL/patients/$PATIENT1_ID/summary?audience=clinician&max_length=500")
SUMMARY=$(echo "$RESPONSE" | jq -r '.summary')
NOTE_COUNT=$(echo "$RESPONSE" | jq -r '.note_count')
PATIENT_NAME=$(echo "$RESPONSE" | jq -r '.heading.name')
if [ "$SUMMARY" != "null" ] && [ -n "$SUMMARY" ]; then
    print_success "Generated clinician summary for $PATIENT_NAME"
    print_info "Note count: $NOTE_COUNT"
    print_info "Summary preview: ${SUMMARY:0:100}..."
else
    print_failure "Failed to generate summary"
    echo "$RESPONSE"
fi

# Synchronous summary - family audience
print_test "GET /patients/{id}/summary?audience=family - Sync summary (family)"
RESPONSE=$(curl -s "$API_URL/patients/$PATIENT1_ID/summary?audience=family&max_length=300")
SUMMARY=$(echo "$RESPONSE" | jq -r '.summary')
if [ "$SUMMARY" != "null" ] && [ -n "$SUMMARY" ]; then
    print_success "Generated family-friendly summary"
    print_info "Summary preview: ${SUMMARY:0:100}..."
else
    print_failure "Failed to generate family summary"
fi

# Asynchronous summary
print_test "POST /patients/{id}/summary/async - Queue async summary"
RESPONSE=$(curl -s -X POST "$API_URL/patients/$PATIENT1_ID/summary/async?audience=clinician")
JOB_ID=$(echo "$RESPONSE" | jq -r '.job_id')
JOB_STATUS=$(echo "$RESPONSE" | jq -r '.status')
if [ "$JOB_ID" != "null" ] && [ -n "$JOB_ID" ]; then
    print_success "Queued async job: ID=$JOB_ID, Status=$JOB_STATUS"
else
    print_failure "Failed to queue async job"
fi

# Check job status endpoint works (don't wait for completion)
if [ -n "$JOB_ID" ] && [ "$JOB_ID" != "null" ]; then
    print_test "GET /patients/{id}/summary/jobs/{job_id} - Check job status endpoint"
    RESPONSE=$(curl -s "$API_URL/patients/$PATIENT1_ID/summary/jobs/$JOB_ID")
    STATUS=$(echo "$RESPONSE" | jq -r '.status')
    if [ -n "$STATUS" ] && [ "$STATUS" != "null" ]; then
        print_success "Job status endpoint works: status=$STATUS"
        print_info "Job will complete in background (check worker logs)"
    else
        print_failure "Failed to get job status"
    fi
fi

# ============================================================================
# ERROR HANDLING
# ============================================================================
print_header "Testing Error Handling"

# Get non-existent patient
print_test "GET /patients/99999 - Non-existent patient (should return 404)"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL/patients/99999")
if [ "$HTTP_CODE" -eq 404 ]; then
    print_success "Correctly returns 404 for non-existent patient"
else
    print_failure "Expected 404, got $HTTP_CODE"
fi

# Create patient with invalid data
print_test "POST /patients - Invalid date format (should return 422)"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$API_URL/patients" \
    -H "Content-Type: application/json" \
    -d '{"name": "Test", "date_of_birth": "invalid-date"}')
if [ "$HTTP_CODE" -eq 422 ]; then
    print_success "Correctly returns 422 for invalid date format"
else
    print_failure "Expected 422, got $HTTP_CODE"
fi

# Create patient with missing required field
print_test "POST /patients - Missing required field (should return 422)"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$API_URL/patients" \
    -H "Content-Type: application/json" \
    -d '{"name": "Test Only"}')
if [ "$HTTP_CODE" -eq 422 ]; then
    print_success "Correctly returns 422 for missing required field"
else
    print_failure "Expected 422, got $HTTP_CODE"
fi

# Invalid pagination
print_test "GET /patients?page=0 - Invalid page number (should return 422)"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL/patients?page=0")
if [ "$HTTP_CODE" -eq 422 ]; then
    print_success "Correctly returns 422 for invalid page number"
else
    print_failure "Expected 422, got $HTTP_CODE"
fi

# ============================================================================
# CLEANUP (Optional)
# ============================================================================
print_header "Cleanup"

# Delete a note
print_test "DELETE /patients/{id}/notes/{note_id} - Delete single note"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X DELETE "$API_URL/patients/$PATIENT1_ID/notes/$NOTE2_ID")
if [ "$HTTP_CODE" -eq 204 ]; then
    print_success "Deleted note $NOTE2_ID"
else
    print_failure "Failed to delete note"
fi

# Delete patient 3
print_test "DELETE /patients/{id} - Delete patient"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X DELETE "$API_URL/patients/$PATIENT3_ID")
if [ "$HTTP_CODE" -eq 204 ]; then
    print_success "Deleted patient $PATIENT3_ID"
else
    print_failure "Failed to delete patient"
fi

# Verify deletion
print_test "GET /patients/{id} - Verify patient deleted"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL/patients/$PATIENT3_ID")
if [ "$HTTP_CODE" -eq 404 ]; then
    print_success "Confirmed patient $PATIENT3_ID is deleted"
else
    print_failure "Patient should be deleted but got $HTTP_CODE"
fi

# ============================================================================
# FINAL REPORT
# ============================================================================
print_header "Test Results Summary"

TOTAL=$((PASSED + FAILED))
echo ""
echo -e "  ${GREEN}Passed: $PASSED${NC}"
echo -e "  ${RED}Failed: $FAILED${NC}"
echo -e "  Total:  $TOTAL"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}  ALL TESTS PASSED! ✓${NC}"
    echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
    exit 0
else
    echo -e "${RED}════════════════════════════════════════════════════════════${NC}"
    echo -e "${RED}  SOME TESTS FAILED ✗${NC}"
    echo -e "${RED}════════════════════════════════════════════════════════════${NC}"
    exit 1
fi
