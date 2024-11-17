import { Box, Stack, Typography } from '@mui/material'
import React, { FC } from 'react'
import Navbar from './partials/Navbar'
import { Outlet } from 'react-router-dom'
interface Props {
	children: React.ReactNode
}

const MainLayout: FC<Props> = ({ children }) => {
	return (
		<>
			<Box
				sx={{
					display: 'flex',
					flexDirection: 'column',
					mx: 'auto',
					minHeight: '95vh',
					alignItems: 'center',
					maxHeight: 'fit-content',
					border: '1px solid red',
					width: '70%',
					maxWidth: '100%',
				}}
			>
				<Stack
					sx={{
						flexDirection: 'row',
						justifyContent: 'center',
						mx: 'auto',
						height: 'fit-content',
						flexWrap: 'nowrap',
						wordBreak: 'none',
						width: '90%',
						textAlign: 'center',
					}}
				>
					<Typography
						variant='h1'
						sx={{
							fontSize: '3rem',
							mt: 1,
							// wordBreak: 'break-word',
							width: 'fit-content',
							border: '1px solid red',
						}}
					>
						Police Radar
					</Typography>
				</Stack>
				<Stack
					sx={{
						width: 'fit-content',
						fontSize: '.5rem',
					}}
				>
					powered by opencv
				</Stack>

				<Navbar />

				<Outlet />
			</Box>
		</>
	)
}

export default MainLayout
