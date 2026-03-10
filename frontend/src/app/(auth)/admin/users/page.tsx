'use client';

import React from 'react';
import { Container, Title, Button, Group, Switch } from '@mantine/core';
import { COLORS, FONTS, GRADIENTS } from '@/utils/theme';
import { useUserManagement } from '@/hooks/useUserManagement';
import { useSystemStats } from '@/hooks/useSystemStats';
import {
  UserTable,
  UserFormModal,
  AccountLimitModal,
  SystemLimitModal,
  SystemStatsPanel,
} from '@/components/features/admin';

export default function UserManagement() {
  const userMgmt = useUserManagement();
  const stats = useSystemStats();

  const isAtLimit = stats.systemLimit <= stats.totalActiveUsers;

  return (
    <Container size="lg" mt="xl">
      <Group justify="space-between" mb="xl">
        <Title order={2} c={COLORS.text} style={{ fontFamily: FONTS.title, fontWeight: 'normal', letterSpacing: '0.05em' }}>ユーザー管理</Title>
        <Group>
          <Switch
            label="削除済みユーザーを表示"
            checked={userMgmt.showDeleted}
            onChange={(event) => userMgmt.setShowDeleted(event.currentTarget.checked)}
          />
          <Button
            onClick={() => userMgmt.setCreateModalOpened(true)}
            variant="gradient"
            gradient={GRADIENTS.adminButton}
            disabled={isAtLimit}
            title={isAtLimit ? 'アカウント制限数に達しているため、新規ユーザーを作成できません' : ''}
          >
            新規ユーザー作成
          </Button>
        </Group>
      </Group>

      {stats.isSuperuser && (
        <SystemStatsPanel
          totalActiveUsers={stats.totalActiveUsers}
          deletedUsersCount={stats.deletedUsersCount}
          systemLimit={stats.systemLimit}
          onEditLimit={() => stats.setSystemLimitModalOpened(true)}
        />
      )}

      <UserTable
        users={userMgmt.users}
        showDeleted={userMgmt.showDeleted}
        onEdit={userMgmt.handleEditUser}
        onDelete={(userId) => userMgmt.handleDeleteUser(userId, stats.fetchSystemStats)}
        formatDate={userMgmt.formatDate}
      />

      {/* 新規ユーザー作成モーダル */}
      <UserFormModal
        mode="create"
        opened={userMgmt.createModalOpened}
        onClose={userMgmt.handleCloseCreateModal}
        name={userMgmt.newUserName}
        onNameChange={userMgmt.setNewUserName}
        email={userMgmt.newUserEmail}
        onEmailChange={userMgmt.setNewUserEmail}
        password={userMgmt.newUserPassword}
        onPasswordChange={userMgmt.setNewUserPassword}
        subscriptionStart={userMgmt.subscriptionStart}
        onSubscriptionStartChange={userMgmt.setSubscriptionStart}
        subscriptionEnd={userMgmt.subscriptionEnd}
        onSubscriptionEndChange={userMgmt.setSubscriptionEnd}
        isAdmin={userMgmt.isAdmin}
        onIsAdminChange={userMgmt.setIsAdmin}
        emailError={userMgmt.emailError}
        dateError={userMgmt.dateError}
        onSubmit={() => userMgmt.handleCreateUser(stats.systemLimit, stats.totalActiveUsers, stats.fetchSystemStats)}
        isAtLimit={isAtLimit}
      />

      {/* ユーザー編集モーダル */}
      <UserFormModal
        mode="edit"
        opened={userMgmt.editModalOpened}
        onClose={userMgmt.handleCloseEditModal}
        name={userMgmt.editName}
        onNameChange={userMgmt.setEditName}
        email={userMgmt.editEmail}
        onEmailChange={userMgmt.setEditEmail}
        password={userMgmt.editPassword}
        onPasswordChange={userMgmt.setEditPassword}
        subscriptionStart={userMgmt.subscriptionStart}
        onSubscriptionStartChange={userMgmt.setSubscriptionStart}
        subscriptionEnd={userMgmt.subscriptionEnd}
        onSubscriptionEndChange={userMgmt.setSubscriptionEnd}
        isAdmin={userMgmt.isAdmin}
        onIsAdminChange={userMgmt.setIsAdmin}
        emailError={userMgmt.emailError}
        dateError={userMgmt.dateError}
        onSubmit={() => userMgmt.handleUpdateUser(stats.fetchSystemStats)}
      />

      {/* アカウント制限数編集モーダル */}
      <AccountLimitModal
        opened={stats.accountLimitModalOpened}
        onClose={stats.handleCloseAccountLimitModal}
        selectedUser={stats.selectedLimitUser}
        accountLimit={stats.accountLimit}
        onAccountLimitChange={stats.setAccountLimit}
        onSubmit={() => stats.handleUpdateAccountLimit(userMgmt.fetchUsers)}
      />

      {/* システム全体の制限数編集モーダル */}
      <SystemLimitModal
        opened={stats.systemLimitModalOpened}
        onClose={() => stats.setSystemLimitModalOpened(false)}
        systemLimit={stats.systemLimit}
        totalActiveUsers={stats.totalActiveUsers}
        onSystemLimitChange={stats.handleSystemLimitChange}
        onSubmit={stats.handleUpdateSystemLimit}
      />
    </Container>
  );
}