<script>
    import { TableSearch, TableHead, TableHeadCell, TableBody, TableBodyRow, TableBodyCell, Button, Badge } from 'flowbite-svelte';
    import { Modal, Heading, Textarea, Select, Label, Input, Alert } from 'flowbite-svelte';
    import { enhance } from '$app/forms';
    import { EditOutline, CloseCircleSolid, PlusOutline } from 'flowbite-svelte-icons';
    import * as m from '$lib/paraglide/messages.js';
    import { languageTag } from '$lib/paraglide/runtime.js';

    import TablePagination from '$lib/components/TablePagination.svelte';
    import ConfirmModal from '$lib/components/ConfirmModal.svelte';
    import SearchableUserList from '$lib/components/SearchableUserList.svelte';
    import { calculateVat } from '$lib/cardPayment.js';

    let { data } = $props();

    function formatAmount(amount) {
        const formattedAmount = amount.toLocaleString('ko-KR', { maximumFractionDigits: 0 });
        return languageTag() === 'ko' ? `${formattedAmount}원` : `KRW ${formattedAmount}`;
    }

    function formatDate(dateStr) {
        if (!dateStr) return '';
        const date = new Date(dateStr);
        return date.toLocaleDateString(languageTag() === 'ko' ? 'ko-KR' : 'en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    }

    function getStatusColor(status) {
        switch (status) {
            case 'completed':
                return 'green';
            case 'cancelled':
                return 'red';
            case 'pending':
                return 'yellow';
            default:
                return 'gray';
        }
    }

    function getStatusText(status) {
        switch (status) {
            case 'completed':
                return m.paymentHistory_statusCompleted();
            case 'cancelled':
                return m.paymentHistory_statusCancelled();
            case 'pending':
                return m.paymentHistory_statusPending();
            default:
                return status;
        }
    }

    function getPaymentTypeText(paymentType) {
        switch (paymentType) {
            case 'card':
                return m.receipt_paymentTypeCard();
            case 'transfer':
                return m.receipt_paymentTypeTransfer();
            case 'cash':
                return m.receipt_paymentTypeCash();
            default:
                return paymentType;
        }
    }

    function getDisplayName(payment) {
        const currentLang = languageTag();
        if (currentLang === 'ko' && payment.attendee_name_ko) {
            return payment.attendee_name_ko;
        }
        return payment.attendee_name;
    }

    function getDisplayInstitute(payment) {
        const currentLang = languageTag();
        if (currentLang === 'ko' && payment.attendee_institute_ko) {
            return payment.attendee_institute_ko;
        }
        return payment.attendee_institute;
    }

    function getDisplayNameWithInstitute(payment) {
        const name = getDisplayName(payment);
        const institute = getDisplayInstitute(payment);
        if (institute) {
            return `${name} (${institute})`;
        }
        return name;
    }

    // Search and pagination
    let searchTerm = $state('');
    let currentPage = $state(1);
    const itemsPerPage = 10;

    let payments = $derived(data.payments || []);

    let filteredPayments = $derived(
        payments.filter((item) =>
            item.attendee_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
            (item.attendee_name_ko && item.attendee_name_ko.includes(searchTerm)) ||
            item.attendee_email.toLowerCase().includes(searchTerm.toLowerCase()) ||
            item.number.toString().includes(searchTerm)
        )
    );

    // Reset to page 1 when search changes
    $effect(() => {
        searchTerm;
        currentPage = 1;
    });

    let totalPages = $derived(Math.ceil(filteredPayments.length / itemsPerPage));
    let paginatedPayments = $derived(
        filteredPayments.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage)
    );

    function handlePageChange(page) {
        currentPage = page;
    }


    // Helper to get attendee display name (for attendee objects, not payment objects)
    function getAttendeeDisplayName(attendee) {
        const currentLang = languageTag();
        if (currentLang === 'ko' && attendee.korean_name) {
            return attendee.korean_name;
        }
        return attendee.name;
    }

    function getAttendeeDisplayInstitute(attendee) {
        const currentLang = languageTag();
        if (currentLang === 'ko' && attendee.institute_ko) {
            return attendee.institute_ko;
        }
        return attendee.institute;
    }

    function getAttendeeDisplayNameWithInstitute(attendee) {
        const name = getAttendeeDisplayName(attendee);
        const institute = getAttendeeDisplayInstitute(attendee);
        if (institute) {
            return `${name} (${institute})`;
        }
        return name;
    }

    // Create payment modal
    let create_modal = $state(false);
    let create_error = $state('');
    let selected_attendee_id = $state(null);
    let payment_amount = $state(data.event.registration_fee || 0);
    let payment_type = $state('card');
    let payment_note = $state('');
    // Card fields
    let card_type = $state('');
    let card_number = $state('');
    let card_vat = $state(0);
    let card_approval_number = $state('');
    let card_installment = $state('single');

    // Recalculate VAT when amount changes (only when modal is open and card payment)
    $effect(() => {
        if (create_modal && payment_type === 'card' && payment_amount > 0) {
            card_vat = calculateVat(payment_amount);
        }
    });

    // Custom getters for SearchableUserList (attendee objects)
    function getAttendeeEmail(attendee) {
        return attendee.user?.email || '';
    }

    const showCreateModal = () => {
        selected_attendee_id = null;
        payment_amount = data.event.registration_fee || 0;
        payment_type = 'card';
        payment_note = '';
        // Reset card fields
        card_type = '';
        card_number = '';
        card_vat = calculateVat(payment_amount);
        card_approval_number = '';
        card_installment = 'single';
        create_error = '';
        create_modal = true;
    };

    const afterCreatePayment = () => {
        return async ({ result, update }) => {
            if (result.type === 'success') {
                await update();
                create_modal = false;
                create_error = '';
            } else {
                create_error = result.error?.message || m.transactions_createError();
            }
        };
    };

    // Note edit modal
    let note_modal = $state(false);
    let note_error = $state('');
    let note_success = $state(false);
    let selected_payment = $state(null);
    let edit_note = $state('');

    const showNoteModal = (payment) => {
        selected_payment = payment;
        edit_note = payment.note || '';
        note_error = '';
        note_success = false;
        note_modal = true;
    };

    const afterUpdateNote = () => {
        return async ({ result, update }) => {
            if (result.type === 'success') {
                await update();
                note_success = true;
                note_error = '';
                setTimeout(() => { note_success = false; }, 2000);
            } else {
                note_error = result.error?.message || m.transactions_noteError();
            }
        };
    };

    // Payment detail modal
    let detail_modal = $state(false);
    let detail_payment = $state(null);

    const showDetailModal = (payment) => {
        detail_payment = payment;
        detail_modal = true;
    };

    // Cancel payment modal
    let cancel_modal = $state(false);
    let cancel_payment = $state(null);
    let cancel_reason = $state('');
    let cancel_error = $state('');
    let cancel_loading = $state(false);

    const showCancelModal = (payment) => {
        cancel_payment = payment;
        cancel_reason = '';
        cancel_error = '';
        cancel_loading = false;
        cancel_modal = true;
    };

    const afterCancelPayment = () => {
        cancel_loading = true;
        return async ({ result, update }) => {
            cancel_loading = false;
            if (result.type === 'success') {
                await update();
                cancel_modal = false;
                cancel_error = '';
            } else {
                cancel_error = result.error?.message || m.transactions_cancelError();
            }
        };
    };

    // Payment type options
    const paymentTypeOptions = [
        { value: 'card', name: m.receipt_paymentTypeCard() },
        { value: 'transfer', name: m.receipt_paymentTypeTransfer() },
        { value: 'cash', name: m.receipt_paymentTypeCash() }
    ];

    // Installment options
    const installmentOptions = [
        { value: 'single', name: m.transactions_installmentSingle() },
        { value: '2', name: m.transactions_installmentMonths({ months: 2 }) },
        { value: '3', name: m.transactions_installmentMonths({ months: 3 }) },
        { value: '4', name: m.transactions_installmentMonths({ months: 4 }) },
        { value: '5', name: m.transactions_installmentMonths({ months: 5 }) },
        { value: '6', name: m.transactions_installmentMonths({ months: 6 }) },
        { value: '12', name: m.transactions_installmentMonths({ months: 12 }) }
    ];

    // Summary stats
    let totalCompleted = $derived(payments.filter(p => p.status === 'completed').reduce((sum, p) => sum + p.amount, 0));
    let totalCancelled = $derived(payments.filter(p => p.status === 'cancelled').reduce((sum, p) => sum + p.amount, 0));
    let countCompleted = $derived(payments.filter(p => p.status === 'completed').length);
    let countCancelled = $derived(payments.filter(p => p.status === 'cancelled').length);
</script>

<Heading tag="h2" class="text-xl font-bold mb-3">{m.transactions_title()}</Heading>
<p class="font-light mb-6">{m.transactions_description()}</p>

<!-- Summary Stats -->
<div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
    <div class="bg-green-50 border border-green-200 rounded-lg p-4">
        <div class="text-sm text-green-600">{m.transactions_completedCount()}</div>
        <div class="text-2xl font-bold text-green-700">{countCompleted}</div>
        <div class="text-sm text-green-600">{formatAmount(totalCompleted)}</div>
    </div>
    <div class="bg-red-50 border border-red-200 rounded-lg p-4">
        <div class="text-sm text-red-600">{m.transactions_cancelledCount()}</div>
        <div class="text-2xl font-bold text-red-700">{countCancelled}</div>
        <div class="text-sm text-red-600">{formatAmount(totalCancelled)}</div>
    </div>
    <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div class="text-sm text-blue-600">{m.transactions_totalCount()}</div>
        <div class="text-2xl font-bold text-blue-700">{payments.length}</div>
    </div>
    <div class="bg-gray-50 border border-gray-200 rounded-lg p-4">
        <div class="text-sm text-gray-600">{m.transactions_netAmount()}</div>
        <div class="text-2xl font-bold text-gray-700">{formatAmount(totalCompleted - totalCancelled)}</div>
    </div>
</div>

<div class="flex justify-end mb-4">
    <Button color="primary" size="sm" onclick={showCreateModal}>
        <PlusOutline class="w-4 h-4 me-2" />
        {m.transactions_createPayment()}
    </Button>
</div>

<TableSearch placeholder={m.transactions_searchPlaceholder()} hoverable={true} bind:inputValue={searchTerm}>
    <TableHead>
        <TableHeadCell>{m.transactions_id()}</TableHeadCell>
        <TableHeadCell>{m.transactions_date()}</TableHeadCell>
        <TableHeadCell>{m.transactions_attendee()}</TableHeadCell>
        <TableHeadCell>{m.transactions_type()}</TableHeadCell>
        <TableHeadCell>{m.transactions_amount()}</TableHeadCell>
        <TableHeadCell>{m.transactions_status()}</TableHeadCell>
        <TableHeadCell>{m.transactions_note()}</TableHeadCell>
        <TableHeadCell class="w-1">{m.transactions_actions()}</TableHeadCell>
    </TableHead>
    <TableBody tableBodyClass="divide-y">
        {#each paginatedPayments as payment}
            <TableBodyRow>
                <TableBodyCell>
                    <button class="text-primary-600 hover:underline cursor-pointer" onclick={() => showDetailModal(payment)}>
                        #{payment.number.toString().padStart(6, '0')}
                    </button>
                </TableBodyCell>
                <TableBodyCell>{formatDate(payment.checkout_date)}</TableBodyCell>
                <TableBodyCell>
                    <div class="font-medium">{getDisplayNameWithInstitute(payment)}</div>
                    <div class="text-sm text-gray-500">{payment.attendee_email}</div>
                </TableBodyCell>
                <TableBodyCell>
                    <Badge color={payment.payment_type === 'card' ? 'blue' : payment.payment_type === 'transfer' ? 'purple' : 'gray'}>
                        {getPaymentTypeText(payment.payment_type)}
                    </Badge>
                </TableBodyCell>
                <TableBodyCell class="font-medium">{formatAmount(payment.amount)}</TableBodyCell>
                <TableBodyCell>
                    <Badge color={getStatusColor(payment.status)}>
                        {getStatusText(payment.status)}
                    </Badge>
                </TableBodyCell>
                <TableBodyCell>
                    <div class="max-w-xs truncate text-sm text-gray-500" title={payment.note}>
                        {payment.note || '-'}
                    </div>
                </TableBodyCell>
                <TableBodyCell>
                    <div class="flex justify-center gap-2">
                        <Button color="none" size="none" onclick={() => showNoteModal(payment)} title={m.transactions_editNote()}>
                            <EditOutline class="w-5 h-5" />
                        </Button>
                        {#if payment.status !== 'cancelled'}
                            <Button color="none" size="none" onclick={() => showCancelModal(payment)} title={m.transactions_cancelPayment()}>
                                <CloseCircleSolid class="w-5 h-5 text-red-500" />
                            </Button>
                        {/if}
                    </div>
                </TableBodyCell>
            </TableBodyRow>
        {/each}
        {#if filteredPayments.length === 0}
            <TableBodyRow>
                <TableBodyCell colspan="8" class="text-center">{m.transactions_noRecords()}</TableBodyCell>
            </TableBodyRow>
        {/if}
    </TableBody>
</TableSearch>

<TablePagination {currentPage} {totalPages} onPageChange={handlePageChange} />

<!-- Create Payment Modal -->
<Modal id="create_payment_modal" size="lg" title={m.transactions_createPayment()} bind:open={create_modal} outsideclose>
    <form method="post" action="?/create_payment" use:enhance={afterCreatePayment}>
        <input type="hidden" name="attendee_id" value={selected_attendee_id || ''} />

        <div class="mb-4">
            <Label class="block mb-2">{m.transactions_selectAttendee()}*</Label>
            <SearchableUserList
                items={data.attendees.filter(a => !data.payments.some(p => p.attendee_id === a.id))}
                bind:selectedId={selected_attendee_id}
                placeholder={m.transactions_searchAttendeePlaceholder()}
                noResultsMessage={m.transactions_noAttendeesFound()}
                getItemName={getAttendeeDisplayName}
                getItemInstitute={getAttendeeDisplayInstitute}
                getItemEmail={getAttendeeEmail}
            />
        </div>
        <div class="grid grid-cols-2 gap-4 mb-4">
            <div>
                <Label for="amount" class="block mb-2">{m.transactions_amount()}*</Label>
                <Input id="amount" name="amount" type="number" bind:value={payment_amount} required />
            </div>
            <div>
                <Label for="payment_type" class="block mb-2">{m.transactions_type()}*</Label>
                <Select id="payment_type" name="payment_type" bind:value={payment_type} items={paymentTypeOptions} required />
            </div>
        </div>

        {#if payment_type === 'card'}
            <div class="border border-gray-200 rounded-lg p-4 mb-4 bg-gray-50">
                <Heading tag="h3" class="text-lg font-semibold mb-4">{m.transactions_cardInfo()}</Heading>
                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <Label for="card_type" class="block mb-2">{m.cardReceipt_cardType()}</Label>
                        <Input id="card_type" name="card_type" type="text" bind:value={card_type} placeholder={m.transactions_cardTypePlaceholder()} />
                    </div>
                    <div>
                        <Label for="card_number" class="block mb-2">{m.cardReceipt_cardNumber()}</Label>
                        <Input id="card_number" name="card_number" type="text" bind:value={card_number} placeholder="1234-56**-****-7890" />
                    </div>
                    <div>
                        <Label for="approval_number" class="block mb-2">{m.cardReceipt_approvalNumber()}</Label>
                        <Input id="approval_number" name="approval_number" type="text" bind:value={card_approval_number} />
                    </div>
                    <div>
                        <Label for="vat" class="block mb-2">{m.cardReceipt_vat()}</Label>
                        <Input id="vat" name="vat" type="number" bind:value={card_vat} />
                    </div>
                    <div>
                        <Label for="installment" class="block mb-2">{m.cardReceipt_installment()}</Label>
                        <Select id="installment" name="installment" bind:value={card_installment} items={installmentOptions} />
                    </div>
                </div>
            </div>
        {/if}

        <div class="mb-4">
            <Label for="note" class="block mb-2">{m.transactions_note()}</Label>
            <Textarea id="note" name="note" bind:value={payment_note} rows="3" placeholder={m.transactions_notePlaceholder()} class="w-full" />
        </div>

        {#if create_error}
            <Alert color="red" class="mb-4">{create_error}</Alert>
        {/if}

        <div class="flex justify-end gap-2">
            <Button color="light" onclick={() => create_modal = false}>{m.common_cancel()}</Button>
            <Button color="primary" type="submit">{m.transactions_create()}</Button>
        </div>
    </form>
</Modal>

<!-- Edit Note Modal -->
<Modal id="note_modal" size="md" title={m.transactions_editNote()} bind:open={note_modal} outsideclose>
    {#if selected_payment}
        <form method="post" action="?/update_payment_note" use:enhance={afterUpdateNote}>
            <input type="hidden" name="id" value={selected_payment.id} />
            <div class="mb-4">
                <p class="text-sm text-gray-500 mb-2">
                    {m.transactions_paymentInfo()}: #{selected_payment.number.toString().padStart(6, '0')} - {getDisplayNameWithInstitute(selected_payment)}
                </p>
            </div>
            <div class="mb-4">
                <Label for="edit_note" class="block mb-2">{m.transactions_note()}</Label>
                <Textarea id="edit_note" name="note" bind:value={edit_note} rows="4" placeholder={m.transactions_notePlaceholder()} class="w-full" />
            </div>

            {#if note_success}
                <Alert color="green" class="mb-4">{m.transactions_noteSuccess()}</Alert>
            {/if}
            {#if note_error}
                <Alert color="red" class="mb-4">{note_error}</Alert>
            {/if}

            <div class="flex justify-end gap-2">
                <Button color="light" onclick={() => note_modal = false}>{m.common_cancel()}</Button>
                <Button color="primary" type="submit">{m.common_save()}</Button>
            </div>
        </form>
    {/if}
</Modal>

<!-- Cancel Payment Modal -->
<Modal id="cancel_payment_modal" size="md" title={m.transactions_cancelPaymentTitle()} bind:open={cancel_modal} outsideclose>
    {#if cancel_payment}
        <form method="post" action="?/cancel_payment" use:enhance={afterCancelPayment}>
            <input type="hidden" name="id" value={cancel_payment.id} />
            <p class="text-sm text-gray-500 mb-4">
                #{cancel_payment.number.toString().padStart(6, '0')} - {getDisplayNameWithInstitute(cancel_payment)} - {formatAmount(cancel_payment.amount)}
            </p>
            <div class="mb-4">
                <Label for="cancel_reason" class="block mb-2">{m.transactions_cancelReason()}</Label>
                <Textarea id="cancel_reason" name="cancel_reason" bind:value={cancel_reason} rows="3" placeholder={m.transactions_cancelReasonPlaceholder()} class="w-full" />
            </div>
            {#if cancel_error}
                <Alert color="red" class="mb-4">{cancel_error}</Alert>
            {/if}
            <div class="flex justify-end gap-2">
                <Button color="light" onclick={() => cancel_modal = false} disabled={cancel_loading}>{m.common_cancel()}</Button>
                <Button color="red" type="submit" disabled={cancel_loading}>{m.transactions_cancelPayment()}</Button>
            </div>
        </form>
    {/if}
</Modal>

<!-- Payment Detail Modal -->
<Modal id="detail_payment_modal" size="lg" title={m.transactions_paymentDetails()} bind:open={detail_modal} outsideclose>
    {#if detail_payment}
        <div class="space-y-4">
            <!-- Order Info -->
            <div class="grid grid-cols-2 gap-4">
                <div>
                    <p class="text-sm font-medium text-gray-500">{m.transactions_id()}</p>
                    <p class="text-base text-gray-900">#{detail_payment.number.toString().padStart(6, '0')}</p>
                </div>
                <div>
                    <p class="text-sm font-medium text-gray-500">{m.transactions_date()}</p>
                    <p class="text-base text-gray-900">{formatDate(detail_payment.checkout_date)}</p>
                </div>
            </div>

            <!-- Attendee Info -->
            <div class="border-t border-gray-200 pt-4">
                <h3 class="text-sm font-semibold text-gray-700 mb-2">{m.transactions_attendee()}</h3>
                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <p class="text-sm font-medium text-gray-500">{m.attendees_name()}</p>
                        <p class="text-base text-gray-900">{getDisplayName(detail_payment)}</p>
                    </div>
                    <div>
                        <p class="text-sm font-medium text-gray-500">{m.attendees_email()}</p>
                        <p class="text-base text-gray-900">{detail_payment.attendee_email}</p>
                    </div>
                    <div>
                        <p class="text-sm font-medium text-gray-500">{m.attendees_institute()}</p>
                        <p class="text-base text-gray-900">{getDisplayInstitute(detail_payment)}</p>
                    </div>
                </div>
            </div>

            <!-- Payment Info -->
            <div class="border-t border-gray-200 pt-4">
                <h3 class="text-sm font-semibold text-gray-700 mb-2">{m.receipt_paymentInfo()}</h3>
                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <p class="text-sm font-medium text-gray-500">{m.transactions_amount()}</p>
                        <p class="text-base font-bold text-gray-900">{formatAmount(detail_payment.amount)}</p>
                    </div>
                    <div>
                        <p class="text-sm font-medium text-gray-500">{m.transactions_type()}</p>
                        <p class="text-base text-gray-900">
                            <Badge color={detail_payment.payment_type === 'card' ? 'blue' : detail_payment.payment_type === 'transfer' ? 'purple' : 'gray'}>
                                {getPaymentTypeText(detail_payment.payment_type)}
                            </Badge>
                        </p>
                    </div>
                    <div>
                        <p class="text-sm font-medium text-gray-500">{m.transactions_status()}</p>
                        <p class="text-base text-gray-900">
                            <Badge color={getStatusColor(detail_payment.status)}>
                                {getStatusText(detail_payment.status)}
                            </Badge>
                        </p>
                    </div>
                </div>
            </div>

            <!-- Note -->
            <div class="border-t border-gray-200 pt-4">
                <h3 class="text-sm font-semibold text-gray-700 mb-2">{m.transactions_note()}</h3>
                <div class="bg-gray-50 rounded-lg p-4 min-h-16">
                    {#if detail_payment.note}
                        <p class="text-gray-700 whitespace-pre-wrap">{detail_payment.note}</p>
                    {:else}
                        <p class="text-gray-400 italic">{m.transactions_noNote()}</p>
                    {/if}
                </div>
            </div>
        </div>

        <div class="flex justify-end gap-2 mt-6">
            <Button color="light" onclick={() => showNoteModal(detail_payment)}>{m.transactions_editNote()}</Button>
            {#if detail_payment.status !== 'cancelled'}
                <Button color="red" onclick={() => { detail_modal = false; showCancelModal(detail_payment); }}>{m.transactions_cancelPayment()}</Button>
            {/if}
            <Button color="primary" onclick={() => detail_modal = false}>{m.common_close()}</Button>
        </div>
    {/if}
</Modal>
