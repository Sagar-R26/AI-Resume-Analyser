import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

class DashboardComponents:
    def render_metric_card(self, label, value, icon=""):
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">{icon}</div>
            <div class="metric-content">
                <div class="metric-value">{value}</div>
                <div class="metric-label">{label}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    def render_gauge_chart(self, value, title, max_val=100):
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=value,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': title, 'font': {'size': 16, 'color': 'white'}},
            number={'font': {'size': 28, 'color': 'white'}, 'suffix': '%'},
            gauge={
                'axis': {'range': [0, max_val], 'tickcolor': 'white'},
                'bar': {'color': "#00d4ff"},
                'bgcolor': '#1e1e1e',
                'borderwidth': 0,
                'steps': [
                    {'range': [0, 40], 'color': '#ff4444'},
                    {'range': [40, 70], 'color': '#ffaa00'},
                    {'range': [70, max_val], 'color': '#00cc66'}
                ]
            }
        ))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font={'color': 'white'},
            height=250,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)

    def render_pie_chart(self, labels, values, title):
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.4,
            marker=dict(colors=px.colors.qualitative.Plotly),
            textfont=dict(color='white')
        )])
        fig.update_layout(
            title=dict(text=title, font=dict(color='white')),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color='white'),
            height=350,
            margin=dict(l=20, r=20, t=40, b=20),
            showlegend=True,
            legend=dict(font=dict(color='white'))
        )
        st.plotly_chart(fig, use_container_width=True)

    def render_line_chart(self, x, y, title):
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=x, y=y,
            mode='lines+markers',
            line=dict(color='#00d4ff', width=2),
            marker=dict(color='#00d4ff', size=6),
            fill='tozeroy',
            fillcolor='rgba(0, 212, 255, 0.1)'
        ))
        fig.update_layout(
            title=dict(text=title, font=dict(color='white')),
            xaxis=dict(title="Date", gridcolor='#333', tickfont=dict(color='white')),
            yaxis=dict(title="Count", gridcolor='#333', tickfont=dict(color='white')),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color='white'),
            height=350,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)

    def render_bar_chart(self, x, y, title):
        fig = go.Figure(data=[
            go.Bar(x=x, y=y, marker=dict(color='#00d4ff'), text=y, textposition='auto')
        ])
        fig.update_layout(
            title=dict(text=title, font=dict(color='white')),
            xaxis=dict(title="Range", gridcolor='#333', tickfont=dict(color='white')),
            yaxis=dict(title="Count", gridcolor='#333', tickfont=dict(color='white')),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color='white'),
            height=350,
            margin=dict(l=20, r=20, t=40, b=20),
            bargap=0.3
        )
        st.plotly_chart(fig, use_container_width=True)
