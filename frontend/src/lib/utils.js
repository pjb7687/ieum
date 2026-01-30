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
