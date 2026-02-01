import { post } from '$lib/fetch';

/** @type {import('./$types').PageServerLoad} */
export async function load({ url }) {
    // Pass through the payment parameters from Toss redirect
    const paymentKey = url.searchParams.get('paymentKey');
    const orderId = url.searchParams.get('orderId');
    const amount = url.searchParams.get('amount');

    return {
        paymentKey,
        orderId,
        amount: amount ? parseInt(amount, 10) : null,
    };
}

/** @type {import('./$types').Actions} */
export const actions = {
    confirm: async ({ request, cookies }) => {
        const formData = await request.formData();
        const paymentKey = formData.get('paymentKey');
        const orderId = formData.get('orderId');
        const amount = parseInt(formData.get('amount'), 10);
        const eventId = parseInt(formData.get('eventId'), 10);

        const response = await post('api/payment/confirm', {
            paymentKey,
            orderId,
            amount,
            eventId,
        }, cookies);

        if (!response.ok) {
            return {
                success: false,
                error: response.data?.message || 'Payment confirmation failed',
            };
        }

        return {
            success: true,
            data: response.data,
        };
    },
};
