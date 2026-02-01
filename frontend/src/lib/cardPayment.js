/**
 * Payment Reference Codes and Utilities
 * Based on Toss Payments API structure
 * Reference: https://docs.tosspayments.com/reference
 */

// =============================================================================
// CARD ISSUER CODES (카드사 코드)
// =============================================================================
const CARD_ISSUERS = {
    '3K': { name: '기업BC', acquirerCode: '3K' },
    '46': { name: '광주은행', acquirerCode: '46' },
    '71': { name: '롯데카드', acquirerCode: '71' },
    '30': { name: '산업은행', acquirerCode: '30' },
    '31': { name: '비씨카드', acquirerCode: '31' },
    '51': { name: '삼성카드', acquirerCode: '51' },
    '38': { name: '새마을금고', acquirerCode: '38' },
    '41': { name: '신한카드', acquirerCode: '41' },
    '62': { name: '신협', acquirerCode: '62' },
    '36': { name: '씨티카드', acquirerCode: '36' },
    '33': { name: '우리BC카드', acquirerCode: '33' },
    'W1': { name: '우리카드', acquirerCode: 'W1' },
    '37': { name: '우체국예금보험', acquirerCode: '37' },
    '39': { name: '저축은행중앙회', acquirerCode: '39' },
    '35': { name: '전북은행', acquirerCode: '35' },
    '42': { name: '제주은행', acquirerCode: '42' },
    '15': { name: '카카오뱅크', acquirerCode: '15' },
    '3A': { name: '케이뱅크', acquirerCode: '3A' },
    '24': { name: '토스뱅크', acquirerCode: '24' },
    '21': { name: '하나카드', acquirerCode: '21' },
    '61': { name: '현대카드', acquirerCode: '61' },
    '11': { name: 'KB국민카드', acquirerCode: '11' },
    '91': { name: 'NH농협카드', acquirerCode: '91' },
    '34': { name: 'Sh수협은행', acquirerCode: '34' },
};

// =============================================================================
// BANK CODES (은행 코드)
// Supports: 가상계좌, 계좌이체, 지급대행
// =============================================================================
const BANKS = {
    '39': { name: '경남은행', nameEn: 'KYONGNAMBANK', officialCode: '039' },
    '34': { name: '광주은행', nameEn: 'GWANGJUBANK', officialCode: '034' },
    '12': { name: '단위농협', nameEn: 'LOCALNONGHYEOP', officialCode: '012' },
    '32': { name: '부산은행', nameEn: 'BUSANBANK', officialCode: '032' },
    '45': { name: '새마을금고', nameEn: 'SAEMAUL', officialCode: '045' },
    '64': { name: '산림조합', nameEn: 'SANLIM', officialCode: '064' },
    '88': { name: '신한은행', nameEn: 'SHINHAN', officialCode: '088' },
    '48': { name: '신협', nameEn: 'SHINHYEOP', officialCode: '048' },
    '27': { name: '씨티은행', nameEn: 'CITI', officialCode: '027' },
    '20': { name: '우리은행', nameEn: 'WOORI', officialCode: '020' },
    '71': { name: '우체국예금보험', nameEn: 'POST', officialCode: '071' },
    '50': { name: '저축은행중앙회', nameEn: 'SAVINGBANK', officialCode: '050' },
    '37': { name: '전북은행', nameEn: 'JEONBUKBANK', officialCode: '037' },
    '35': { name: '제주은행', nameEn: 'JEJUBANK', officialCode: '035' },
    '90': { name: '카카오뱅크', nameEn: 'KAKAOBANK', officialCode: '090' },
    '89': { name: '케이뱅크', nameEn: 'KBANK', officialCode: '089' },
    '92': { name: '토스뱅크', nameEn: 'TOSSBANK', officialCode: '092' },
    '81': { name: '하나은행', nameEn: 'HANA', officialCode: '081' },
    '54': { name: '홍콩상하이은행', nameEn: 'HSBC', officialCode: '054' },
    '60': { name: 'Bank of America', nameEn: 'BOA', officialCode: '060' },
    '03': { name: 'IBK기업은행', nameEn: 'IBK', officialCode: '003' },
    '06': { name: 'KB국민은행', nameEn: 'KOOKMIN', officialCode: '004' },
    '31': { name: 'iM뱅크(대구)', nameEn: 'DAEGUBANK', officialCode: '031' },
    '02': { name: '한국산업은행', nameEn: 'KDBBANK', officialCode: '002' },
    '11': { name: 'NH농협은행', nameEn: 'NONGHYEOP', officialCode: '011' },
    '23': { name: 'SC제일은행', nameEn: 'SC', officialCode: '023' },
    '07': { name: 'Sh수협은행', nameEn: 'SUHYEOP', officialCode: '007' },
    '30': { name: '수협중앙회', nameEn: 'SUHYEOPLOCALBANK', officialCode: '030' },
};

// Banks that support virtual account issuance (가상계좌 발급 가능 은행)
const VIRTUAL_ACCOUNT_BANKS = ['39', '34', '06', '03', '11', '31', '32', '45', '07', '88', '20', '71', '81'];

// =============================================================================
// SECURITIES COMPANY CODES (증권사 코드)
// =============================================================================
const SECURITIES = {
    'S8': { name: '교보증권', nameEn: 'KYOBO_SECURITIES', officialCode: '261' },
    'SE': { name: '대신증권', nameEn: 'DAISHIN_SECURITIES', officialCode: '267' },
    'SK': { name: '메리츠증권', nameEn: 'MERITZ_SECURITIES', officialCode: '287' },
    'S5': { name: '미래에셋증권', nameEn: 'MIRAE_ASSET_SECURITIES', officialCode: '238' },
    'SM': { name: '부국증권', nameEn: 'BOOKOOK_SECURITIES', officialCode: '290' },
    'S3': { name: '삼성증권', nameEn: 'SAMSUNG_SECURITIES', officialCode: '240' },
    'SN': { name: '신영증권', nameEn: 'SHINYOUNG_SECURITIES', officialCode: '291' },
    'S2': { name: '신한금융투자', nameEn: 'SHINHAN_SECURITIES', officialCode: '278' },
    'S0': { name: '유안타증권', nameEn: 'YUANTA_SECURITES', officialCode: '209' },
    'SJ': { name: '유진투자증권', nameEn: 'EUGENE_INVESTMENT_AND_SECURITIES', officialCode: '280' },
    'SQ': { name: '카카오페이증권', nameEn: 'KAKAOPAY_SECURITIES', officialCode: '288' },
    'SB': { name: '키움증권', nameEn: 'KIWOOM', officialCode: '264' },
    'ST': { name: '토스증권', nameEn: 'TOSS_SECURITIES', officialCode: '271' },
    'SR': { name: '펀드온라인코리아', nameEn: 'KOREA_FOSS_SECURITIES', officialCode: '294' },
    'SH': { name: '하나금융투자', nameEn: 'HANA_INVESTMENT_AND_SECURITIES', officialCode: '270' },
    'S9': { name: '아이엠증권', nameEn: 'HI_INVESTMENT_AND_SECURITIES', officialCode: '262' },
    'S6': { name: '한국투자증권', nameEn: 'KOREA_INVESTMENT_AND_SECURITIES', officialCode: '243' },
    'SG': { name: '한화투자증권', nameEn: 'HANHWA_INVESTMENT_AND_SECURITIES', officialCode: '269' },
    'SA': { name: '현대차증권', nameEn: 'HYUNDAI_MOTOR_SECURITIES', officialCode: '263' },
    'SI': { name: 'DB금융투자', nameEn: 'DB_INVESTMENT_AND_SECURITIES', officialCode: '279' },
    'S4': { name: 'KB증권', nameEn: 'KB_SECURITIES', officialCode: '218' },
    'SP': { name: 'KTB투자증권', nameEn: 'DAOL_INVESTMENT_AND_SECURITIES', officialCode: '227' },
    'SO': { name: 'LIG투자증권', nameEn: 'LIG_INVESTMENT_AND_SECURITIES', officialCode: '292' },
    'SL': { name: 'NH투자증권', nameEn: 'NH_INVESTMENT_AND_SECURITIES', officialCode: '247' },
    'SD': { name: 'SK증권', nameEn: 'SK_SECURITIES', officialCode: '266' },
};

// =============================================================================
// EASY PAY PROVIDER CODES (간편결제사 코드)
// =============================================================================
const EASY_PAY_PROVIDERS = {
    'TOSSPAY': { name: '토스페이' },
    'NAVERPAY': { name: '네이버페이' },
    'SAMSUNGPAY': { name: '삼성페이' },
    'APPLEPAY': { name: '애플페이' },
    'LPAY': { name: '엘페이' },
    'KAKAOPAY': { name: '카카오페이' },
    'PINPAY': { name: '핀페이' },
    'PAYCO': { name: '페이코' },
    'SSG': { name: 'SSG페이' },
};

// =============================================================================
// TELECOM CARRIER CODES (통신사 코드)
// For mobile phone billing (휴대폰 결제)
// =============================================================================
const TELECOM_CARRIERS = {
    'KT': { name: 'KT' },
    'LGU': { name: 'LG 유플러스' },
    'SKT': { name: 'SK 텔레콤' },
    'HELLO': { name: 'LG 헬로모바일' },
    'KCT': { name: '티플러스' },
    'SK7': { name: 'SK 세븐모바일' },
};

// =============================================================================
// PAYMENT STATUS CONSTANTS
// =============================================================================

// Card types
export const CARD_TYPES = ['신용', '체크', '기프트', '미확인'];

// Owner types
export const OWNER_TYPES = ['개인', '법인', '미확인'];

// Acquire status values
export const ACQUIRE_STATUS = {
    READY: 'READY',
    REQUESTED: 'REQUESTED',
    COMPLETED: 'COMPLETED',
    CANCEL_REQUESTED: 'CANCEL_REQUESTED',
    CANCELED: 'CANCELED',
};

// Payment status values
export const PAYMENT_STATUS = {
    READY: 'READY',
    IN_PROGRESS: 'IN_PROGRESS',
    WAITING_FOR_DEPOSIT: 'WAITING_FOR_DEPOSIT',
    DONE: 'DONE',
    CANCELED: 'CANCELED',
    PARTIAL_CANCELED: 'PARTIAL_CANCELED',
    ABORTED: 'ABORTED',
    EXPIRED: 'EXPIRED',
};

// =============================================================================
// UTILITY FUNCTIONS
// =============================================================================

/**
 * Calculate VAT from total amount
 * VAT = (결제 금액 - 면세 금액) / 11, rounded
 */
export function calculateVat(totalAmount, taxFreeAmount = 0) {
    return Math.round((totalAmount - taxFreeAmount) / 11);
}

/**
 * Calculate supplied amount (공급가액)
 * suppliedAmount = totalAmount - vat
 */
export function calculateSuppliedAmount(totalAmount, taxFreeAmount = 0) {
    const vat = calculateVat(totalAmount, taxFreeAmount);
    return totalAmount - vat;
}

// =============================================================================
// LOOKUP FUNCTIONS
// =============================================================================

/**
 * Get card issuer name by code
 * @param {string} issuerCode - The issuer code
 * @returns {string} Issuer name
 */
export function getIssuerName(issuerCode) {
    return CARD_ISSUERS[issuerCode]?.name || '알 수 없음';
}

/**
 * Get list of available card issuers
 * @returns {Array} Array of {code, name} objects
 */
export function getCardIssuers() {
    return Object.entries(CARD_ISSUERS).map(([code, data]) => ({
        code,
        name: data.name,
    }));
}

/**
 * Get bank name by code
 * @param {string} bankCode - The bank code
 * @returns {string} Bank name
 */
export function getBankName(bankCode) {
    return BANKS[bankCode]?.name || '알 수 없음';
}

/**
 * Get list of available banks
 * @returns {Array} Array of {code, name, nameEn} objects
 */
export function getBanks() {
    return Object.entries(BANKS).map(([code, data]) => ({
        code,
        name: data.name,
        nameEn: data.nameEn,
    }));
}

/**
 * Get list of banks that support virtual account issuance
 * @returns {Array} Array of {code, name, nameEn} objects
 */
export function getVirtualAccountBanks() {
    return VIRTUAL_ACCOUNT_BANKS.map(code => ({
        code,
        name: BANKS[code]?.name || code,
        nameEn: BANKS[code]?.nameEn || code,
    }));
}

/**
 * Get list of available easy pay providers
 * @returns {Array} Array of {code, name} objects
 */
export function getEasyPayProviders() {
    return Object.entries(EASY_PAY_PROVIDERS).map(([code, data]) => ({
        code,
        name: data.name,
    }));
}

/**
 * Get list of available telecom carriers
 * @returns {Array} Array of {code, name} objects
 */
export function getTelecomCarriers() {
    return Object.entries(TELECOM_CARRIERS).map(([code, data]) => ({
        code,
        name: data.name,
    }));
}

/**
 * Get list of available securities companies
 * @returns {Array} Array of {code, name, nameEn} objects
 */
export function getSecurities() {
    return Object.entries(SECURITIES).map(([code, data]) => ({
        code,
        name: data.name,
        nameEn: data.nameEn,
    }));
}
