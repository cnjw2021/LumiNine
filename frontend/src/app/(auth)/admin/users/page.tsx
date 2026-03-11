'use client';


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
        onEditAccountLimit={
          stats.isSuperuser
            ? (user) => {
              stats.setSelectedLimitUser(user);
              stats.setAccountLimit(user.account_limit || 0);
              stats.setAccountLimitModalOpened(true);
            }
            : undefined
        }
        formatDate={userMgmt.formatDate}
      />

      {/* 新規ユーザー作成モーダル */}
      <UserFormModal
        mode="create"
        opened={userMgmt.createModalOpened}
        onClose={userMgmt.handleCloseCreateModal}
        name={userMgmt.createForm.fields.name}
        onNameChange={userMgmt.createForm.setName}
        email={userMgmt.createForm.fields.email}
        onEmailChange={userMgmt.createForm.setEmail}
        password={userMgmt.createForm.fields.password}
        onPasswordChange={userMgmt.createForm.setPassword}
        subscriptionStart={userMgmt.createForm.fields.subscriptionStart}
        onSubscriptionStartChange={userMgmt.createForm.setSubscriptionStart}
        subscriptionEnd={userMgmt.createForm.fields.subscriptionEnd}
        onSubscriptionEndChange={userMgmt.createForm.setSubscriptionEnd}
        isAdmin={userMgmt.createForm.fields.isAdmin}
        onIsAdminChange={userMgmt.createForm.setIsAdmin}
        emailError={userMgmt.createForm.errors.emailError}
        dateError={userMgmt.createForm.errors.dateError}
        onSubmit={() => userMgmt.handleCreateUser(stats.systemLimit, stats.totalActiveUsers, stats.fetchSystemStats)}
        isAtLimit={isAtLimit}
        isSuperuser={stats.isSuperuser}
      />

      {/* ユーザー編集モーダル */}
      <UserFormModal
        mode="edit"
        opened={userMgmt.editModalOpened}
        onClose={userMgmt.handleCloseEditModal}
        name={userMgmt.editForm.fields.name}
        onNameChange={userMgmt.editForm.setName}
        email={userMgmt.editForm.fields.email}
        onEmailChange={userMgmt.editForm.setEmail}
        password={userMgmt.editForm.fields.password}
        onPasswordChange={userMgmt.editForm.setPassword}
        subscriptionStart={userMgmt.editForm.fields.subscriptionStart}
        onSubscriptionStartChange={userMgmt.editForm.setSubscriptionStart}
        subscriptionEnd={userMgmt.editForm.fields.subscriptionEnd}
        onSubscriptionEndChange={userMgmt.editForm.setSubscriptionEnd}
        isAdmin={userMgmt.editForm.fields.isAdmin}
        onIsAdminChange={userMgmt.editForm.setIsAdmin}
        emailError={userMgmt.editForm.errors.emailError}
        dateError={userMgmt.editForm.errors.dateError}
        onSubmit={() => userMgmt.handleUpdateUser(stats.fetchSystemStats)}
        isSuperuser={stats.isSuperuser}
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