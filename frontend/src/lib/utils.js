import { languageTag } from '$lib/paraglide/runtime.js';

/**
 * Get the display name for an institution based on the current UI language
 * Works with both User objects (institute_en/institute_ko) and Attendee objects (institute/institute_ko)
 * @param {Object} obj - User or Attendee object
 * @returns {string} - Institution name in the appropriate language
 */
export function getDisplayInstitute(obj) {
    const currentLang = languageTag();
    if (currentLang === 'ko' && obj.institute_ko) {
        return obj.institute_ko;
    }
    // For User objects, use institute_en; for Attendee objects, use institute
    return obj.institute_en || obj.institute || '';
}

/**
 * Get the display name for a person based on the current UI language
 * Works with both User and Attendee objects
 * @param {Object} obj - User or Attendee object
 * @returns {string} - Person's name in the appropriate language
 */
export function getDisplayName(obj) {
    const currentLang = languageTag();
    if (currentLang === 'ko' && obj.korean_name) {
        return obj.korean_name;
    }
    return obj.name || '';
}

/**
 * Get the display venue for an event based on the current UI language
 * @param {Object} event - Event object
 * @returns {string} - Venue name in the appropriate language
 */
export function getDisplayVenue(event) {
    const currentLang = languageTag();
    if (currentLang === 'ko' && event.venue_ko) {
        return event.venue_ko;
    }
    return event.venue || '';
}

/**
 * Get the display organizers for an event based on the current UI language
 * @param {Object} event - Event object
 * @returns {string} - Formatted organizers string in the appropriate language
 * Format: "Name (Institution), Name (Institution)"
 */
export function getDisplayOrganizers(event) {
    const currentLang = languageTag();
    if (currentLang === 'ko' && event.organizers_ko) {
        return event.organizers_ko;
    }
    return event.organizers_en || '';
}

/**
 * Format a date string based on the current UI language
 * @param {string} dateString - Date string in YYYY-MM-DD format
 * @returns {string} - Formatted date
 * Korean: 2026.04.22
 * English: Apr 22, 2026
 */
export function formatDate(dateString) {
    if (!dateString) return '';

    const currentLang = languageTag();
    const date = new Date(dateString + 'T00:00:00'); // Add time to avoid timezone issues

    if (currentLang === 'ko') {
        // Korean format: 2026.04.22
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        return `${year}.${month}.${day}`;
    } else {
        // English format: Apr 22, 2026
        const options = { year: 'numeric', month: 'short', day: 'numeric' };
        return date.toLocaleDateString('en-US', options);
    }
}

/**
 * Format a date range based on the current UI language
 * @param {string} startDate - Start date in YYYY-MM-DD format
 * @param {string} endDate - End date in YYYY-MM-DD format
 * @returns {string} - Formatted date range
 * Korean: 2026.04.22 ~ 2026.04.30
 * English: Apr 22, 2026 - Apr 30, 2026
 */
export function formatDateRange(startDate, endDate) {
    if (!startDate || !endDate) return '';

    const currentLang = languageTag();
    const separator = currentLang === 'ko' ? ' ~ ' : ' - ';

    return formatDate(startDate) + separator + formatDate(endDate);
}
