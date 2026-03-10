import React from 'react';
import {
    Modal,
    Stack,
    TextInput,
    PasswordInput,
    Switch,
    Button,
    Group,
    Text,
} from '@mantine/core';
import CustomDatePicker from '@/components/common/ui/Datepicker';
import { GRADIENTS } from '@/utils/theme';
import type { DateError } from '@/types/admin';

interface UserFormModalProps {
    mode: 'create' | 'edit';
    opened: boolean;
    onClose: () => void;

    // フォーム値
    name: string;
    onNameChange: (v: string) => void;
    email: string;
    onEmailChange: (v: string) => void;
    password: string;
    onPasswordChange: (v: string) => void;
    subscriptionStart: string;
    onSubscriptionStartChange: (v: string) => void;
    subscriptionEnd: string;
    onSubscriptionEndChange: (v: string) => void;
    isAdmin: boolean;
    onIsAdminChange: (v: boolean) => void;

    // エラー
    emailError: string;
    dateError: DateError;

    // アクション
    onSubmit: () => void;

    // 作成モード用: システム上限チェック
    isAtLimit?: boolean;
}

export function UserFormModal({
    mode,
    opened,
    onClose,
    name,
    onNameChange,
    email,
    onEmailChange,
    password,
    onPasswordChange,
    subscriptionStart,
    onSubscriptionStartChange,
    subscriptionEnd,
    onSubscriptionEndChange,
    isAdmin,
    onIsAdminChange,
    emailError,
    dateError,
    onSubmit,
    isAtLimit = false,
}: UserFormModalProps) {
    const isCreate = mode === 'create';
    const title = isCreate ? '新規ユーザー作成' : 'ユーザー情報の編集';
    const submitLabel = isCreate ? '作成' : '更新';

    return (
        <Modal
            opened={opened}
            onClose={onClose}
            title={title}
            size="md"
        >
            <Stack>
                {isCreate && isAtLimit && (
                    <Text c="red" size="sm" fw={500} mb="md">
                        アカウント制限数に達しているため、新規ユーザーを作成できません。
                        制限数を増やすか、不要なアカウントを削除してください。
                    </Text>
                )}
                <TextInput
                    label="名前"
                    placeholder="ユーザー名を入力"
                    value={name}
                    onChange={(event) => onNameChange(event.currentTarget.value)}
                    required
                />
                <TextInput
                    label="メールアドレス"
                    placeholder="example@example.com"
                    value={email}
                    onChange={(event) => onEmailChange(event.currentTarget.value)}
                    error={emailError}
                    required
                />
                <PasswordInput
                    label={isCreate ? 'パスワード' : 'パスワード（変更する場合のみ）'}
                    value={password}
                    onChange={(event) => onPasswordChange(event.currentTarget.value)}
                    error={password.length > 0 && password.length < 8 ? 'パスワードは8文字以上である必要があります' : ''}
                    required={isCreate}
                />
                <CustomDatePicker
                    label="利用開始日"
                    value={subscriptionStart}
                    onChange={onSubscriptionStartChange}
                    error={dateError.startDate}
                />
                <CustomDatePicker
                    label="利用終了日"
                    value={subscriptionEnd}
                    onChange={onSubscriptionEndChange}
                    error={dateError.endDate}
                />
                <Switch
                    label="管理者権限"
                    checked={isAdmin}
                    onChange={(event) => onIsAdminChange(event.currentTarget.checked)}
                />
                {emailError && (
                    <Text c="red" size="sm">
                        {emailError}
                    </Text>
                )}
                <Group justify="flex-end" mt="md">
                    <Button variant="light" onClick={onClose}>
                        キャンセル
                    </Button>
                    <Button
                        onClick={onSubmit}
                        variant="gradient"
                        gradient={GRADIENTS.adminButton}
                        disabled={isCreate && isAtLimit}
                    >
                        {submitLabel}
                    </Button>
                </Group>
            </Stack>
        </Modal>
    );
}
